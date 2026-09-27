# Run the framework's checks in the framework's build environment, from PowerShell.
#
#     docker/dev/check.ps1                            the whole suite
#     docker/dev/check.ps1 python3 -m tests.floor     the quality floor alone
#     docker/dev/check.ps1 python3 -m pytest -k ruff  anything else
#
# ⭐ The twin of `check`, for a contributor on Windows (a register direction: the
# framework is worked on from Windows too, on Docker Desktop). It runs the same
# image, named by the same identity, with the same bound, and needs Docker and
# PowerShell, which Windows ships, and nothing else. ⛔ Every rule is argued once,
# in `check`; this file says only where it differs, and
# `tests/docker/test_dev_check_ps1.py` holds the two to one command.
#
# ⭐ The variables are the same and set the PowerShell way:
#
#     $env:STUDYFORGE_VISUAL = 'required'; docker/dev/check.ps1
#     $env:STUDYFORGE_CHECK_TIMEOUT = '300'; docker/dev/check.ps1
#
# ⛔ No path from this machine is written into any file. `$Root` is derived from
# where this script sits.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# The repository root: this file is at <root>/docker/dev/check.ps1.
$Root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path

# ⚠️ WHERE IT DIFFERS: the uid and gid. POSIX has `id`; Windows has no uid at all.
# An already-set value wins, as in `check`; then `id`, where the host has one;
# then 1000, the first ordinary user of the image's base. ⭐ On Docker Desktop for
# Windows a bind's files belong to the Windows user whatever uid writes them, so
# the value only has to be an ordinary user who can write the checkout, and
# never root.
function Get-Owner([string] $Flag) {
    if (Get-Command id -CommandType Application -ErrorAction SilentlyContinue) {
        return (& id $Flag).Trim()
    }
    return '1000'
}
if (-not $env:STUDYFORGE_UID) { $env:STUDYFORGE_UID = Get-Owner '-u' }
if (-not $env:STUDYFORGE_GID) { $env:STUDYFORGE_GID = Get-Owner '-g' }

# ⛔ Unconditional, for `check`'s reason: no build provenance.
$env:BUILDX_NO_DEFAULT_ATTESTATIONS = '1'

# ⛔ The image is named by its inputs: `check`'s identity, derived in the same
# pinned base, over the same files. ⚠️ WHERE IT DIFFERS: the script run in there
# carries no double quote, which Windows PowerShell 5.1 strips from an argument
# it hands a program; it hashes the same listing, so it prints the same identity.
$INPUTS = 'pyproject.toml README.md'
$Base = ''
foreach ($line in Get-Content -LiteralPath (Join-Path $Root 'docker/dev/Dockerfile')) {
    if ($line.StartsWith('FROM ')) { $Base = ($line.Substring(5) -split ' ')[0] }
}
$Identify = @'
set -eu; { find docker/dev -type f | LC_ALL=C sort; for input; do echo $input; done; } | tr '\n' '\0' | xargs -0 sha256sum -- | sha256sum
'@.Trim()
$derived = & docker run --rm --network none `
    --user "$($env:STUDYFORGE_UID):$($env:STUDYFORGE_GID)" `
    --volume "$($Root):/inputs:ro" --workdir /inputs $Base `
    sh -c $Identify identity @($INPUTS -split ' ')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$identity = ("$derived" -split ' ')[0]
if ($identity -notmatch '^[0-9a-f]+$') {
    [Console]::Error.WriteLine('docker/dev/check: no identity derived from the build inputs')
    exit 1
}
$env:STUDYFORGE_DEV_IDENTITY = $identity

[Console]::Error.WriteLine("docker/dev/check: image studyforge/dev:inputs-$identity")

# ⚠️ WHERE IT DIFFERS: a linked worktree's git directory. `check` mounts it at its
# own absolute path, which is a path inside the container only where the host's
# is POSIX. ⭐ Here too, where it is (PowerShell on Linux or macOS); on Windows
# nothing is added and the tests that ask git skip rather than lie. A plain
# clone needs none of this.
$gitMount = @()
if ((Test-Path -LiteralPath (Join-Path $Root '.git') -PathType Leaf) -and
    (Get-Command git -CommandType Application -ErrorAction SilentlyContinue)) {
    $common = (& git -C $Root rev-parse --git-common-dir 2>$null)
    if ($LASTEXITCODE -eq 0 -and "$common".StartsWith('/')) {
        $gitMount = @('--volume', "$($common):$($common):ro")
    }
}

# ⛔ The outer bound, inside the container, as in `check`.
$timeout = if ($env:STUDYFORGE_CHECK_TIMEOUT) { $env:STUDYFORGE_CHECK_TIMEOUT } else { '1800' }

$command = @($args)
if ($command.Count -eq 0) {
    $command = @('python3', '-m', 'pytest')
}

& docker compose --file (Join-Path $Root 'docker/dev/compose.yaml') `
    run --rm --build @gitMount dev `
    timeout --kill-after=30s $timeout @command
exit $LASTEXITCODE
