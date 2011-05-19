drop table if exists pages;
create table pages (
  page_path string primary key,
  page_text string not null
);

drop table if exists page_history;
create table page_history (
  history_id integer primary key autoincrement,
  page_path string not null,
  page_text string not null,
  updated timestamp default current_timestamp
);
