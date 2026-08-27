# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PerfSample(models.Model):
    _name = 'perf.sample'

    name = fields.Char()
    value = fields.Integer()

    def bad_method(self):
        # 错误示范：循环内查询
        for i in range(10):
            records = self.env['perf.sample'].search([('name', '=', 'test')])
            records.write({'value': i})

    def good_method(self):
        # 正确示范：批处理
        self.write({'value': 100})

    @api.depends('name')
    def _compute_value(self):
        for record in self:
            # 错误示范：遗漏依赖项 (未在 depends 中声明 value_raw)
            record.value = record.value_raw * 2
