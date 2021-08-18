from odoo import api, fields, models, _


class sale_custom(models.Model):
    _inherit="sale.order.line"
    note_sale=fields.Char('ملاحظات')
    analytical_account_id=fields.Many2one(related='order_id.analytic_account_id',string="الحساب التحليلي")

    
   
    

class purchase_custom(models.Model):
    _inherit="purchase.order.line"
    note_purchase=fields.Char('ملاحظات')
class sale_order_custom(models.Model):
    _inherit='sale.order'
    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        # sales_order=self.env['sale.order'].search([])
        # for order in sales_order:
        #
        #     for rec in order.picking_ids:
        #         stock=self.env['stock.move'].search([('picking_id','=',rec.id)])
        #
        #         for st in stock:
        #             st.write({
        #               'date':order.date_order })


        for order in self:
            order.delivery_count = len(order.picking_ids)
            for rec in order.picking_ids:
                stock=self.env['stock.move'].search([('picking_id','=',rec.id)])
                for st in stock:
                    st.write({
                      'date':order.date_order })

                 


     
            
             

 
                  
             
         
        
 
    