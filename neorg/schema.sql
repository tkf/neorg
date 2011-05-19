drop table if exists pages;
create table pages (
  page_path string primary key,
  page_text string not null
);
