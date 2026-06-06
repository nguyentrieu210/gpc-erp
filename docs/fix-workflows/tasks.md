# Tasks — Fix Workflows GPC ERP

## Task 1: Fix HR Payroll GL

- [ ] 1.1 Fix run_payroll — build earnings deductions tren slip object truoc insert
- [ ] 1.2 Xac nhan submit_salary_slip post GL Dr642 Cr334
- [ ] 1.3 Verify GL Entry ton tai sau submit slip

## Task 2: Fix Kinh doanh partial delivery va return

- [ ] 2.1 Fix create_delivery_note them param sales_order dung ERPNext mapper
- [ ] 2.2 Them make_sales_return delivery_note_name
- [ ] 2.3 Them make_credit_note invoice_name
- [ ] 2.4 Them get_so_status tra per_delivered per_billed linked docs

## Task 3: Fix CRM Sales integration

- [ ] 3.1 convert_opportunity_to_customer ghi custom_crm_opportunity len Customer
- [ ] 3.2 Them setup_crm_integration idempotent tao custom field
- [ ] 3.3 Them get_customer_crm_context customer_name
- [ ] 3.4 kinhdoanh api get_customer them crm_opportunity field

## Task 4: Fix Tai chinh GL integration

- [ ] 4.1 get_gl_entries them voucher_type options cho filter
- [ ] 4.2 Them get_gl_summary from_date to_date group theo voucher_type
- [ ] 4.3 Them get_voucher_gl voucher_type voucher_no drill down chung tu
- [ ] 4.4 Them get_account_statement account from_date to_date
- [ ] 4.5 Cap nhat get_accounting_dashboard them recent_vouchers voucher_breakdown
