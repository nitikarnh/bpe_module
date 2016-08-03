drop function  IF EXISTS purchase_barcode();
drop type IF EXISTS ean13record;

CREATE TYPE ean13record AS (id bigint, barcode varchar, code varchar);

CREATE OR REPLACE FUNCTION purchase_barcode()
RETURNS setof ean13record AS $$
declare
	r ean13record % rowtype;
	po record;
begin
    for po in select purchase_order.id, purchase_order_line.product_id, round(purchase_order_line.product_qty)  as product_qty from purchase_order join purchase_order_line on purchase_order.id = purchase_order_line.order_id loop 
	for i in 1..po.product_qty loop
		for r in select po.id, ean13, default_code from product_product pp
			 join product_template pt on pt.id = pp.product_tmpl_id
			 where sale_ok = True and type not in ('service') and pp.active = True
			       and pp.id = po.product_id loop
			 return next r;
		end loop;
	end loop;
    end loop;
    return;
END;
$$ LANGUAGE plpgsql;
