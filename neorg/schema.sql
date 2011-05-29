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
  page_exists integer not null default 1,
  updated timestamp default current_timestamp
);

drop table if exists system_info;
create table system_info (
  version string primary key,
  updated timestamp default current_timestamp
);
