#!/usr/bin/perl
# The live runner: runs one allowed argv with the reader's own API key in THAT process's environment.
#
# Written by studyforge's execution skill and mounted read-only into the live runner, a compose
# service in the `live` profile only. It publishes no port. It listens on the internal network the
# study server shares with it, and its only way out is the egress proxy (a second internal network).
# The graded runner's service (runservice.pl) is a different file and has no `live` verb: it cannot
# be given a key.
#
# The key is a FIELD of the request, never an argument. This script puts it in the environment of
# the one child it forks, under the variable the corpus declared (STUDYFORGE_LIVE_KEY_NAME holds the
# NAME only). The service's own environment has no key, and neither has the process list, a file,
# a log or an error text: it prints nothing about a request. What the child writes is scanned
# for the key, its URL-encoded and its base64 forms, and a hit is replaced before a byte leaves.
#
# The wire, as studyforge.execute.live speaks it:
#   request  fields each ended by NUL, then one more NUL
#            live <STUDYFORGE_RUN=token> <cwd> <key> <argv...>
#            stop <STUDYFORGE_RUN=token> <TERM|KILL>
#            ping
#   answer   live: "O<n>\n" + n bytes, repeated; then "X<status>\n"
#            stop: "stopped\n"   ping: "pong\n"   refused: "X126\n" after one O frame saying why
#
# Perl, and only modules perl-base ships.
use strict;
use warnings;
use IO::Socket::INET;
use POSIX qw(_exit dup2 setsid);
use Fcntl qw(:flock);

$SIG{__WARN__} = sub { };   # a warning could carry a value; this service says nothing of requests

my $PORT    = $ENV{STUDYFORGE_LIVE_PORT} // 7124;
my $BIND    = $ENV{STUDYFORGE_LIVE_BIND} || '0.0.0.0';
my $WORK    = $ENV{STUDYFORGE_RUN_WORK} || '/work';
my $ALLOWED = "$WORK/.studyforge/execution/allowed/live";
my $NAME    = $ENV{STUDYFORGE_LIVE_KEY_NAME} // '';
my $LIMIT   = $ENV{STUDYFORGE_LIVE_TIMEOUT} // 300;
my $CAP     = $ENV{STUDYFORGE_LIVE_MAX_OUTPUT} // (1 << 20);
my $LOCK    = $ENV{STUDYFORGE_LIVE_LOCK} // '/tmp/studyforge-live.lock';
my %SIGNALS = (TERM => 'TERM', KILL => 'KILL');
my $TOKEN   = qr/\ASTUDYFORGE_RUN=[0-9a-f]{32}\z/;
my $KEY     = qr/\A[A-Za-z0-9_-]{8,256}\z/;
my $MAX     = 1 << 20;
my $MARKER  = '[redacted]';
my @B64 = ('A' .. 'Z', 'a' .. 'z', 0 .. 9, '+', '/');

die "live runner: STUDYFORGE_LIVE_KEY_NAME must name a variable\n" if $NAME !~ /\A[A-Z][A-Z0-9_]{0,63}\z/;

$SIG{CHLD} = 'IGNORE';
$SIG{PIPE} = 'IGNORE';

my $server = IO::Socket::INET->new(
    LocalAddr => $BIND, LocalPort => $PORT, Listen => 4, ReuseAddr => 1, Proto => 'tcp',
) or die "live runner: cannot listen on $PORT: $!\n";
print STDERR 'live runner: listening on ' . $server->sockport . "\n";

while (1) {
    my $client = $server->accept or next;
    my $pid = fork;
    if (!defined $pid) { close $client; next }
    if ($pid == 0) { close $server; serve($client); _exit(0) }
    close $client;
}

sub serve {
    my ($client) = @_;
    my $data = '';
    while ($data !~ /\x00\x00/ && length($data) < $MAX) {
        my $read = sysread($client, my $chunk, 65536);
        last if !$read;
        $data .= $chunk;
    }
    return if $data !~ /\A(.*?\x00)\x00/s;
    my @fields = split /\x00/, $1, -1;
    pop @fields;
    $data = '';
    my $kind = shift @fields // '';
    if ($kind eq 'ping') { send_all($client, "pong\n"); return }
    if ($kind eq 'stop') { stop(@fields); send_all($client, "stopped\n"); return }
    if ($kind eq 'live') { live($client, @fields); return }
    refuse($client, 'this service runs live requests only');
}

sub send_all {
    my ($client, $bytes) = @_;
    while (length $bytes) {
        my $sent = syswrite $client, $bytes;
        return 0 if !defined $sent;
        substr($bytes, 0, $sent) = '';
    }
    return 1;
}

sub refuse {
    my ($client, $why) = @_;
    my $line = "live runner: $why\n";
    send_all($client, 'O' . length($line) . "\n" . $line . "X126\n");
}

sub allowed {
    my ($entry) = @_;
    open my $fh, '<:raw', $ALLOWED or return 0;
    local $/;
    my $list = <$fh>;
    close $fh;
    return 0 if !defined $list;
    for my $one (split /(?<=\x00\x00)/, $list) {
        return 1 if $one eq $entry;
    }
    return 0;
}

sub base64 {
    my ($bytes) = @_;
    my $out = '';
    for (my $at = 0; $at < length $bytes; $at += 3) {
        my $chunk = substr($bytes, $at, 3);
        my $n = length $chunk;
        my $bits = 0;
        $bits = ($bits << 8) | ord(substr($chunk, $_, 1)) for 0 .. $n - 1;
        $bits <<= 8 * (3 - $n);
        my @six = map { ($bits >> (18 - 6 * $_)) & 63 } 0 .. 3;
        $out .= join '', map { $B64[$_] } @six[0 .. $n];
        $out .= '=' x (3 - $n);
    }
    return $out;
}

# Every form of the key a stream must not carry: raw, URL-encoded (a key of this charset encodes to
# itself), and its base64 at each of the three alignments, trimmed to the characters that do not
# depend on a neighbour, with the URL-safe spelling of each. Longest first.
sub forms_of {
    my ($key) = @_;
    my %forms = ($key => 1);
    my $whole = base64($key);
    (my $bare = $whole) =~ s/=+\z//;
    for my $spelling ($whole, $bare) {
        $forms{$spelling} = 1;
        (my $safe = $spelling) =~ tr{+/}{-_};
        $forms{$safe} = 1;
    }
    for my $pad (0 .. 2) {
        my $encoded = base64(("\0" x $pad) . $key);
        $encoded =~ s/=+\z//;
        my $head = (0, 2, 3)[$pad];
        my $tail = (length($key) + $pad) % 3;
        my $body = $tail
            ? substr($encoded, $head, length($encoded) - 1 - $head)
            : substr($encoded, $head);
        next if length($body) < 8;
        $forms{$body} = 1;
        (my $safe = $body) =~ tr{+/}{-_};
        $forms{$safe} = 1;
    }
    return sort { length($b) <=> length($a) || $a cmp $b } keys %forms;
}

# How many characters at the end of `$buf` are the beginning of a form of the key and so must wait
# for the next chunk to say whether they finish it; everything before them is safe to send now.
sub unfinished {
    my ($buf, @forms) = @_;
    my $keep = 0;
    for my $form (@forms) {
        my $most = length($form) - 1;
        $most = length($buf) if $most > length($buf);
        for (my $k = $most; $k > $keep; $k--) {
            if (substr($buf, -$k) eq substr($form, 0, $k)) { $keep = $k; last }
        }
    }
    return $keep;
}

sub live {
    my ($client, $token, $cwd, $key, @argv) = @_;
    if (!defined $token || $token !~ $TOKEN || !defined $cwd || !defined $key || !@argv) {
        return refuse($client, 'a live run names a token, a directory, a key and an argv');
    }
    return refuse($client, 'the key is not in the form a live run accepts') if $key !~ $KEY;
    if ($cwd ne '.' && ($cwd =~ m{\A/} || grep { $_ eq '' || $_ eq '.' || $_ eq '..' } split m{/}, $cwd, -1)) {
        return refuse($client, 'a run\'s directory is relative to the corpus and never climbs out');
    }
    my $entry = join('', map { "$_\x00" } $cwd, @argv) . "\x00";
    return refuse($client, 'this argv is not one the corpus\'s records declare live') if !allowed($entry);
    open my $lock, '>', $LOCK or return refuse($client, 'no lock');
    return refuse($client, 'a live run is already going') if !flock($lock, LOCK_EX | LOCK_NB);
    my @forms = forms_of($key);
    pipe(my $out, my $in) or return refuse($client, 'no pipe');
    local $SIG{CHLD} = 'DEFAULT';
    my $pid = fork;
    return refuse($client, 'no process') if !defined $pid;
    if ($pid == 0) {
        close $out; close $client;
        setsid();
        open STDIN, '<', '/dev/null';
        dup2(fileno($in), 1);
        dup2(fileno($in), 2);
        close $in;
        chdir($cwd eq '.' ? $WORK : "$WORK/$cwd") or _exit(127);
        $ENV{PYTHONDONTWRITEBYTECODE} = '1';
        $ENV{PYTHONUNBUFFERED} = '1';
        my ($var, $value) = split /=/, $token, 2;
        $ENV{$var} = $value;
        $ENV{$NAME} = $key;       # THE ONE PLACE the key is put in an environment: this child's.
        { no warnings 'exec'; exec { $argv[0] } @argv; }
        print STDERR "$argv[0]: the program could not be started (is it on PATH?)\n";
        _exit(127);
    }
    close $in;
    my ($hold, $total, $status) = ('', 0, undef);
    my $deadline = time + $LIMIT;
    my $gone = 0;
    my $emit = sub {
        my ($bytes) = @_;
        return if !length $bytes || $gone;
        $total += length $bytes;
        if (!send_all($client, 'O' . length($bytes) . "\n" . $bytes)) { $gone = 1; kill 'KILL', -$pid }
    };
    my $rin = '';
    vec($rin, fileno($out), 1) = 1;
    while (1) {
        my $left = $deadline - time;
        if ($left <= 0) {
            kill 'KILL', -$pid;
            $emit->("live runner: the run was stopped at its time limit\n");
            $status = 124;
            last;
        }
        my $ready = select(my $rout = $rin, undef, undef, $left < 1 ? $left : 1);
        next if !$ready;
        my $read = sysread($out, my $chunk, 65536);
        last if !$read;
        my $buf = $hold . $chunk;
        $buf =~ s/\Q$_\E/$MARKER/g for @forms;
        my $keep = unfinished($buf, @forms);
        $emit->(substr($buf, 0, length($buf) - $keep));
        $hold = substr($buf, length($buf) - $keep);
        if ($total > $CAP) {
            kill 'KILL', -$pid;
            $emit->("\nlive runner: the run was stopped at its output limit\n");
            $status = 1;
            $hold = '';
            last;
        }
    }
    if (length $hold) {
        my $buf = $hold;
        $buf =~ s/\Q$_\E/$MARKER/g for @forms;
        $emit->($buf);
    }
    close $out;
    kill 'KILL', -$pid;       # the run's whole process group is gone when the run ends
    waitpid($pid, 0);
    $status = $? & 127 ? 128 + ($? & 127) : $? >> 8 if !defined $status;
    send_all($client, "X$status\n") if !$gone;
    flock($lock, LOCK_UN);
}

sub stop {
    my ($token, $name) = @_;
    return if !defined $token || $token !~ $TOKEN || !defined $name || !$SIGNALS{$name};
    opendir my $proc, '/proc' or return;
    for my $pid (grep { /\A\d+\z/ } readdir $proc) {
        next if $pid == $$;
        open my $fh, '<:raw', "/proc/$pid/environ" or next;
        local $/;
        my $environ = <$fh> // '';
        close $fh;
        kill $SIGNALS{$name}, $pid if grep { $_ eq $token } split /\x00/, $environ;
    }
    closedir $proc;
}
