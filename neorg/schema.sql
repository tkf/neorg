drop table if exists pages;
create table pages (
  pagepath string primary key,
  pagetext string not null
);
