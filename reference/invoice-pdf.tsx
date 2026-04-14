/**
 * Invoice/Receipt PDF Template
 * Usage: Downloadable invoices, receipts, payment records
 * 
 * Dependencies: @react-pdf/renderer
 * 
 * Props:
 * - invoiceNumber: string - Invoice reference number
 * - invoiceDate: string - Invoice date
 * - dueDate: string - Payment due date
 * - type: 'invoice' | 'receipt' | 'quote' - Document type
 * - company: object - Your company details
 * - customer: object - Customer details
 * - items: Array<{description, quantity, unitPrice, total}> - Line items
 * - totals: object - Price breakdown
 * - notes: string - Additional notes
 * - paymentInfo: object - Bank/payment details
 */

import {
  Document,
  Page,
  Text,
  View,
  StyleSheet,
  Font,
} from '@react-pdf/renderer'

// Register fonts (optional - use web-safe fonts or custom fonts)
Font.register({
  family: 'Inter',
  fonts: [
    { src: 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hjp-Ek-_EeA.woff', fontWeight: 400 },
    { src: 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuI6fAZ9hjp-Ek-_EeA.woff', fontWeight: 600 },
    { src: 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuFuYAZ9hjp-Ek-_EeA.woff', fontWeight: 700 },
  ],
})

interface InvoiceItem {
  description: string
  quantity: number
  unitPrice: number
  total: number
}

interface Company {
  name: string
  logo?: string
  address: string
  city: string
  state: string
  zipCode: string
  country: string
  email: string
  phone: string
  website?: string
  taxId?: string
}

interface Customer {
  name: string
  company?: string
  email: string
  address: string
  city: string
  state: string
  zipCode: string
  country: string
}

interface InvoiceTotals {
  subtotal: number
  discount?: number
  discountLabel?: string
  tax: number
  taxRate: number
  shipping?: number
  total: number
}

interface PaymentInfo {
  bankName?: string
  accountName?: string
  accountNumber?: string
  routingNumber?: string
  swiftCode?: string
  paypalEmail?: string
  notes?: string
}

interface InvoicePDFProps {
  invoiceNumber: string
  invoiceDate: string
  dueDate?: string
  type: 'invoice' | 'receipt' | 'quote'
  company: Company
  customer: Customer
  items: InvoiceItem[]
  totals: InvoiceTotals
  notes?: string
  paymentInfo?: PaymentInfo
  currency?: string
}

const styles = StyleSheet.create({
  page: {
    fontFamily: 'Inter',
    fontSize: 10,
    padding: 40,
    backgroundColor: '#ffffff',
  },
  // Header
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 40,
  },
  companyInfo: {
    maxWidth: '50%',
  },
  companyName: {
    fontSize: 20,
    fontWeight: 700,
    color: '#1a1a1a',
    marginBottom: 8,
  },
  companyDetails: {
    fontSize: 9,
    color: '#6b7280',
    lineHeight: 1.5,
  },
  invoiceTitle: {
    textAlign: 'right',
  },
  invoiceType: {
    fontSize: 28,
    fontWeight: 700,
    color: '#1a1a1a',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  invoiceNumber: {
    fontSize: 10,
    color: '#6b7280',
    marginTop: 4,
  },
  // Info Section
  infoSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 30,
  },
  infoBlock: {
    maxWidth: '45%',
  },
  infoLabel: {
    fontSize: 8,
    fontWeight: 600,
    color: '#9ca3af',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  infoValue: {
    fontSize: 10,
    color: '#374151',
    lineHeight: 1.5,
  },
  customerName: {
    fontWeight: 600,
    color: '#1a1a1a',
    marginBottom: 2,
  },
  invoiceDetails: {
    backgroundColor: '#f9fafb',
    padding: 16,
    borderRadius: 6,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  detailLabel: {
    fontSize: 9,
    color: '#6b7280',
  },
  detailValue: {
    fontSize: 9,
    fontWeight: 600,
    color: '#1a1a1a',
  },
  // Table
  table: {
    marginBottom: 30,
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#1a1a1a',
    padding: 10,
    borderRadius: 4,
  },
  tableHeaderText: {
    fontSize: 8,
    fontWeight: 600,
    color: '#ffffff',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
    padding: 12,
    alignItems: 'center',
  },
  tableRowAlt: {
    backgroundColor: '#fafafa',
  },
  colDescription: {
    flex: 4,
  },
  colQty: {
    flex: 1,
    textAlign: 'center',
  },
  colPrice: {
    flex: 1.5,
    textAlign: 'right',
  },
  colTotal: {
    flex: 1.5,
    textAlign: 'right',
  },
  itemDescription: {
    fontSize: 10,
    color: '#1a1a1a',
    fontWeight: 600,
  },
  itemText: {
    fontSize: 10,
    color: '#4b5563',
  },
  // Totals
  totalsSection: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginBottom: 30,
  },
  totalsBox: {
    width: 250,
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6,
  },
  totalLabel: {
    fontSize: 10,
    color: '#6b7280',
  },
  totalValue: {
    fontSize: 10,
    color: '#1a1a1a',
  },
  totalDivider: {
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
    marginVertical: 8,
  },
  grandTotalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    backgroundColor: '#f9fafb',
    padding: 12,
    borderRadius: 4,
  },
  grandTotalLabel: {
    fontSize: 12,
    fontWeight: 700,
    color: '#1a1a1a',
  },
  grandTotalValue: {
    fontSize: 14,
    fontWeight: 700,
    color: '#1a1a1a',
  },
  // Notes & Payment
  bottomSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  notesSection: {
    flex: 1,
    marginRight: 20,
  },
  paymentSection: {
    flex: 1,
    backgroundColor: '#f9fafb',
    padding: 16,
    borderRadius: 6,
  },
  sectionTitle: {
    fontSize: 10,
    fontWeight: 600,
    color: '#1a1a1a',
    marginBottom: 8,
  },
  notesText: {
    fontSize: 9,
    color: '#6b7280',
    lineHeight: 1.6,
  },
  paymentText: {
    fontSize: 9,
    color: '#374151',
    marginBottom: 4,
  },
  paymentLabel: {
    color: '#6b7280',
  },
  // Footer
  footer: {
    position: 'absolute',
    bottom: 30,
    left: 40,
    right: 40,
    textAlign: 'center',
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
    paddingTop: 20,
  },
  footerText: {
    fontSize: 8,
    color: '#9ca3af',
    marginBottom: 4,
  },
  // Status badges
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    alignSelf: 'flex-start',
    marginTop: 8,
  },
  paidBadge: {
    backgroundColor: '#dcfce7',
  },
  pendingBadge: {
    backgroundColor: '#fef3c7',
  },
  statusText: {
    fontSize: 8,
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  paidText: {
    color: '#166534',
  },
  pendingText: {
    color: '#92400e',
  },
})

const formatCurrency = (amount: number, currency: string = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount)
}

export function InvoicePDF({
  invoiceNumber = 'INV-2024-001',
  invoiceDate = new Date().toLocaleDateString(),
  dueDate = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString(),
  type = 'invoice',
  company = {
    name: 'Your Company Name',
    address: '123 Business Street',
    city: 'San Francisco',
    state: 'CA',
    zipCode: '94107',
    country: 'United States',
    email: 'billing@yourcompany.com',
    phone: '+1 (555) 123-4567',
    website: 'www.yourcompany.com',
    taxId: 'TAX-123456789',
  },
  customer = {
    name: 'John Doe',
    company: 'Customer Company',
    email: 'john@customer.com',
    address: '456 Customer Ave',
    city: 'New York',
    state: 'NY',
    zipCode: '10001',
    country: 'United States',
  },
  items = [
    { description: 'Product or Service 1', quantity: 2, unitPrice: 150.00, total: 300.00 },
    { description: 'Product or Service 2', quantity: 1, unitPrice: 250.00, total: 250.00 },
    { description: 'Product or Service 3', quantity: 3, unitPrice: 75.00, total: 225.00 },
  ],
  totals = {
    subtotal: 775.00,
    discount: 50.00,
    discountLabel: '10% Early Bird',
    tax: 58.00,
    taxRate: 8,
    shipping: 15.00,
    total: 798.00,
  },
  notes = 'Thank you for your business! Payment is due within 30 days of invoice date. Late payments may incur a 1.5% monthly fee.',
  paymentInfo = {
    bankName: 'First National Bank',
    accountName: 'Your Company Inc',
    accountNumber: '****4567',
    routingNumber: '****8901',
    paypalEmail: 'payments@yourcompany.com',
  },
  currency = 'USD',
}: InvoicePDFProps) {
  const typeLabels = {
    invoice: 'Invoice',
    receipt: 'Receipt',
    quote: 'Quote',
  }

  const isPaid = type === 'receipt'

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.companyInfo}>
            <Text style={styles.companyName}>{company.name}</Text>
            <Text style={styles.companyDetails}>
              {company.address}{'\n'}
              {company.city}, {company.state} {company.zipCode}{'\n'}
              {company.country}{'\n'}
              {company.email}{'\n'}
              {company.phone}
              {company.taxId && `\nTax ID: ${company.taxId}`}
            </Text>
          </View>
          <View style={styles.invoiceTitle}>
            <Text style={styles.invoiceType}>{typeLabels[type]}</Text>
            <Text style={styles.invoiceNumber}>#{invoiceNumber}</Text>
            {isPaid && (
              <View style={[styles.statusBadge, styles.paidBadge]}>
                <Text style={[styles.statusText, styles.paidText]}>Paid</Text>
              </View>
            )}
            {!isPaid && type === 'invoice' && (
              <View style={[styles.statusBadge, styles.pendingBadge]}>
                <Text style={[styles.statusText, styles.pendingText]}>Pending</Text>
              </View>
            )}
          </View>
        </View>

        {/* Bill To & Invoice Details */}
        <View style={styles.infoSection}>
          <View style={styles.infoBlock}>
            <Text style={styles.infoLabel}>Bill To</Text>
            <Text style={styles.customerName}>{customer.name}</Text>
            {customer.company && (
              <Text style={styles.infoValue}>{customer.company}</Text>
            )}
            <Text style={styles.infoValue}>
              {customer.address}{'\n'}
              {customer.city}, {customer.state} {customer.zipCode}{'\n'}
              {customer.country}{'\n'}
              {customer.email}
            </Text>
          </View>
          <View style={styles.invoiceDetails}>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Invoice Date:</Text>
              <Text style={styles.detailValue}>{invoiceDate}</Text>
            </View>
            {dueDate && type !== 'receipt' && (
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Due Date:</Text>
                <Text style={styles.detailValue}>{dueDate}</Text>
              </View>
            )}
            {type === 'receipt' && (
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Payment Date:</Text>
                <Text style={styles.detailValue}>{invoiceDate}</Text>
              </View>
            )}
            <View style={[styles.detailRow, { marginBottom: 0 }]}>
              <Text style={styles.detailLabel}>Amount Due:</Text>
              <Text style={styles.detailValue}>
                {isPaid ? formatCurrency(0, currency) : formatCurrency(totals.total, currency)}
              </Text>
            </View>
          </View>
        </View>

        {/* Items Table */}
        <View style={styles.table}>
          {/* Table Header */}
          <View style={styles.tableHeader}>
            <Text style={[styles.tableHeaderText, styles.colDescription]}>Description</Text>
            <Text style={[styles.tableHeaderText, styles.colQty]}>Qty</Text>
            <Text style={[styles.tableHeaderText, styles.colPrice]}>Unit Price</Text>
            <Text style={[styles.tableHeaderText, styles.colTotal]}>Total</Text>
          </View>

          {/* Table Rows */}
          {items.map((item, index) => (
            <View 
              key={index} 
              style={[styles.tableRow, index % 2 === 1 && styles.tableRowAlt]}
            >
              <Text style={[styles.itemDescription, styles.colDescription]}>
                {item.description}
              </Text>
              <Text style={[styles.itemText, styles.colQty]}>{item.quantity}</Text>
              <Text style={[styles.itemText, styles.colPrice]}>
                {formatCurrency(item.unitPrice, currency)}
              </Text>
              <Text style={[styles.itemText, styles.colTotal]}>
                {formatCurrency(item.total, currency)}
              </Text>
            </View>
          ))}
        </View>

        {/* Totals */}
        <View style={styles.totalsSection}>
          <View style={styles.totalsBox}>
            <View style={styles.totalRow}>
              <Text style={styles.totalLabel}>Subtotal</Text>
              <Text style={styles.totalValue}>{formatCurrency(totals.subtotal, currency)}</Text>
            </View>

            {totals.discount && (
              <View style={styles.totalRow}>
                <Text style={styles.totalLabel}>
                  Discount {totals.discountLabel && `(${totals.discountLabel})`}
                </Text>
                <Text style={[styles.totalValue, { color: '#16a34a' }]}>
                  -{formatCurrency(totals.discount, currency)}
                </Text>
              </View>
            )}

            {totals.shipping !== undefined && (
              <View style={styles.totalRow}>
                <Text style={styles.totalLabel}>Shipping</Text>
                <Text style={styles.totalValue}>
                  {totals.shipping === 0 ? 'FREE' : formatCurrency(totals.shipping, currency)}
                </Text>
              </View>
            )}

            <View style={styles.totalRow}>
              <Text style={styles.totalLabel}>Tax ({totals.taxRate}%)</Text>
              <Text style={styles.totalValue}>{formatCurrency(totals.tax, currency)}</Text>
            </View>

            <View style={styles.totalDivider} />

            <View style={styles.grandTotalRow}>
              <Text style={styles.grandTotalLabel}>Total</Text>
              <Text style={styles.grandTotalValue}>{formatCurrency(totals.total, currency)}</Text>
            </View>
          </View>
        </View>

        {/* Notes & Payment Info */}
        <View style={styles.bottomSection}>
          {notes && (
            <View style={styles.notesSection}>
              <Text style={styles.sectionTitle}>Notes</Text>
              <Text style={styles.notesText}>{notes}</Text>
            </View>
          )}

          {paymentInfo && type !== 'receipt' && (
            <View style={styles.paymentSection}>
              <Text style={styles.sectionTitle}>Payment Information</Text>
              {paymentInfo.bankName && (
                <Text style={styles.paymentText}>
                  <Text style={styles.paymentLabel}>Bank: </Text>
                  {paymentInfo.bankName}
                </Text>
              )}
              {paymentInfo.accountName && (
                <Text style={styles.paymentText}>
                  <Text style={styles.paymentLabel}>Account Name: </Text>
                  {paymentInfo.accountName}
                </Text>
              )}
              {paymentInfo.accountNumber && (
                <Text style={styles.paymentText}>
                  <Text style={styles.paymentLabel}>Account #: </Text>
                  {paymentInfo.accountNumber}
                </Text>
              )}
              {paymentInfo.routingNumber && (
                <Text style={styles.paymentText}>
                  <Text style={styles.paymentLabel}>Routing #: </Text>
                  {paymentInfo.routingNumber}
                </Text>
              )}
              {paymentInfo.paypalEmail && (
                <Text style={styles.paymentText}>
                  <Text style={styles.paymentLabel}>PayPal: </Text>
                  {paymentInfo.paypalEmail}
                </Text>
              )}
            </View>
          )}
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Thank you for your business!
          </Text>
          <Text style={styles.footerText}>
            {company.website && `${company.website} • `}{company.email} • {company.phone}
          </Text>
        </View>
      </Page>
    </Document>
  )
}

export default InvoicePDF
