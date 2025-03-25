select count(*) from record;

select * from record;

select r.family, count(r.family) as c from record r group by r.family order by c;

