select count(*) from record;

select r.barcode, r.images from record r;

select r.family, count(r.family) as c from record r group by r.family order by c;

