/* The search index built in the page, for a site whose build could not build it.

   ⚠️ **WRITTEN ONLY WITHOUT `node`.** A build precompiles the index under `node` and the search
   part loads it as it is (`search.js`); this file is written beside it only when that failed, and
   the build said so. It turns the records the index then holds (versions 1 and 2) into a ranked
   index here, in chunks, so the box stays usable while it fills.

   ⭐ A large course writes its records in shards beside the index, which then holds only the page
   table and the shard names. They are loaded one after the other and joined in order, so a
   record's number is the same as in one file. A text that repeats an earlier record's is written
   as that record's number and put back here, so the words indexed and shown are the page's own. */

(function () {
  'use strict';

  window.studyforge = window.studyforge || {};

  function restored(records) {
    records.forEach(function (record) {
      if (typeof record[3] === 'number') { record[3] = records[record[3]][3]; }
    });
  }

  function joined(data, script, done, failed) {
    if (!data.shards) { if (data.records) { done(); } else { failed(); } return; }
    var names = data.shards;
    var records = [];
    (function next(at) {
      if (at === names.length) { data.records = records; done(); return; }
      script(names[at], function () {
        var part = window.studyforge.searchShards && window.studyforge.searchShards[names[at]];
        if (!part) { failed(); return; }
        records = records.concat(part);
        next(at + 1);
      }, failed);
    }(0));
  }

  /* Load `data`'s shards with `script`, build its index and call `done(engine, entry)`,
     `entry(hit)` naming the record a hit is: its page, address, title, trail, heading, anchor
     and text. */
  window.studyforge.searchBuild = function (data, searchOptions, script, done, failed) {
    joined(data, script, function () {
      restored(data.records);
      var engine = new window.MiniSearch({
        fields: ['title', 'heading', 'text'], searchOptions: searchOptions
      });
      var docs = data.records.map(function (record, id) {
        return { id: id, title: data.pages[record[0]][1], heading: record[1], text: record[3] };
      });
      engine.addAllAsync(docs, { chunkSize: 300 }).then(function () {
        done(engine, function (hit) {
          var record = data.records[hit.id];
          var page = data.pages[record[0]];
          return { key: record[0], url: page[0], title: page[1], trail: page[2],
            heading: record[1], anchor: record[2], text: record[3] };
        });
      }, failed);
    }, failed);
  };
}());
