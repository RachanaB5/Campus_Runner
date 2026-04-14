/**
 * Invoice/Receipt Email Template
 * Usage: Payment confirmations, invoices, refund receipts
 * 
 * Dependencies: @react-email/components
 * 
 * Props:
 * - customerName: string - Customer's display name
 * - invoiceNumber: string - Invoice reference number
 * - invoiceDate: string - Invoice date
 * - dueDate: string - Payment due date (for invoices)
 * - type: 'invoice' | 'receipt' | 'refund' - Document type
 * - items: Array<{description, quantity, unitPrice, total}> - Line items
 * - paymentMethod: object - Payment details
 * - billingAddress: object - Billing address
 * - totals: object - Price breakdown
 */

import {
  Body,
  Button,
  Column,
  Container,
  Head,
  Heading,
  Hr,
  Html,
  Img,
  Link,
  Preview,
  Row,
  Section,
  Text,
} from '@react-email/components'

interface InvoiceItem {
  description: string
  quantity: number
  unitPrice: number
  total: number
}

interface PaymentMethod {
  type: 'card' | 'paypal' | 'bank' | 'wallet'
  last4?: string
  brand?: string
  email?: string
}

interface BillingAddress {
  name: string
  company?: string
  street: string
  city: string
  state: string
  zipCode: string
  country: string
}

interface InvoiceTotals {
  subtotal: number
  tax: number
  taxRate: number
  discount?: number
  discountCode?: string
  total: number
  amountPaid?: number
  amountDue?: number
}

interface InvoiceReceiptEmailProps {
  customerName: string
  customerEmail: string
  invoiceNumber: string
  invoiceDate: string
  dueDate?: string
  type: 'invoice' | 'receipt' | 'refund'
  items: InvoiceItem[]
  paymentMethod?: PaymentMethod
  billingAddress: BillingAddress
  totals: InvoiceTotals
  companyName: string
  companyLogo?: string
  companyAddress?: string
  supportEmail: string
  invoiceUrl: string
  pdfUrl?: string
}

const typeConfig = {
  invoice: {
    title: 'Invoice',
    preview: 'Invoice for your order',
    color: '#1a1a1a',
    bgColor: '#f9fafb',
  },
  receipt: {
    title: 'Receipt',
    preview: 'Payment receipt - Thank you!',
    color: '#16a34a',
    bgColor: '#f0fdf4',
  },
  refund: {
    title: 'Refund Confirmation',
    preview: 'Your refund has been processed',
    color: '#dc2626',
    bgColor: '#fef2f2',
  },
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount)
}

const getPaymentIcon = (type: PaymentMethod['type']) => {
  switch (type) {
    case 'card': return '💳'
    case 'paypal': return '🅿️'
    case 'bank': return '🏦'
    case 'wallet': return '👛'
    default: return '💰'
  }
}

export function InvoiceReceiptEmail({
  customerName = 'Customer',
  customerEmail = 'customer@example.com',
  invoiceNumber = 'INV-2024-001',
  invoiceDate = new Date().toLocaleDateString(),
  dueDate,
  type = 'receipt',
  items = [
    { description: 'Sample Product', quantity: 1, unitPrice: 99.99, total: 99.99 },
  ],
  paymentMethod = { type: 'card', last4: '0000', brand: 'Card' },
  billingAddress = {
    name: 'John Doe',
    street: '123 Main St',
    city: 'New York',
    state: 'NY',
    zipCode: '10001',
    country: 'United States',
  },
  totals = {
    subtotal: 99.99,
    tax: 8.50,
    taxRate: 8.5,
    total: 108.49,
  },
  companyName = 'Your Store',
  companyLogo,
  companyAddress = '456 Business Ave, Suite 100, San Francisco, CA 94107',
  supportEmail = 'support@yourstore.com',
  invoiceUrl = 'https://yourstore.com/invoices/INV-2024-001',
  pdfUrl,
}: InvoiceReceiptEmailProps) {
  const config = typeConfig[type]

  return (
    <Html>
      <Head />
      <Preview>{config.preview} - {invoiceNumber}</Preview>
      <Body style={main}>
        <Container style={container}>
          {/* Header */}
          <Section style={header}>
            <Row>
              <Column>
                {companyLogo ? (
                  <Img src={companyLogo} width="120" height="40" alt={companyName} />
                ) : (
                  <Text style={logoText}>{companyName}</Text>
                )}
              </Column>
              <Column style={{ textAlign: 'right' as const }}>
                <Text style={{ ...documentType, color: config.color }}>
                  {config.title.toUpperCase()}
                </Text>
              </Column>
            </Row>
          </Section>

          {/* Status Banner (for receipts/refunds) */}
          {type !== 'invoice' && (
            <Section style={{ ...statusBanner, backgroundColor: config.bgColor }}>
              <Text style={{ ...statusText, color: config.color }}>
                {type === 'receipt' ? '✓ Payment Successful' : '↩ Refund Processed'}
              </Text>
              <Text style={{ ...amountText, color: config.color }}>
                {formatCurrency(totals.total)}
              </Text>
            </Section>
          )}

          {/* Main Content */}
          <Section style={content}>
            <Text style={greeting}>Hi {customerName},</Text>
            
            <Text style={paragraph}>
              {type === 'invoice' && `Please find your invoice below. Payment is due by ${dueDate || 'receipt'}.`}
              {type === 'receipt' && 'Thank you for your purchase! Here\'s your receipt for your records.'}
              {type === 'refund' && 'Your refund has been processed. Here\'s your confirmation for your records.'}
            </Text>

            {/* Invoice Details */}
            <Section style={detailsBox}>
              <Row>
                <Column>
                  <Text style={detailLabel}>Invoice Number</Text>
                  <Text style={detailValue}>{invoiceNumber}</Text>
                </Column>
                <Column>
                  <Text style={detailLabel}>Date</Text>
                  <Text style={detailValue}>{invoiceDate}</Text>
                </Column>
                {dueDate && type === 'invoice' && (
                  <Column>
                    <Text style={detailLabel}>Due Date</Text>
                    <Text style={detailValue}>{dueDate}</Text>
                  </Column>
                )}
              </Row>
            </Section>

            <Hr style={divider} />

            {/* Line Items Table */}
            <Section style={tableSection}>
              {/* Table Header */}
              <Row style={tableHeader}>
                <Column style={colDescription}>
                  <Text style={tableHeaderText}>Description</Text>
                </Column>
                <Column style={colQty}>
                  <Text style={tableHeaderText}>Qty</Text>
                </Column>
                <Column style={colPrice}>
                  <Text style={tableHeaderText}>Price</Text>
                </Column>
                <Column style={colTotal}>
                  <Text style={tableHeaderText}>Total</Text>
                </Column>
              </Row>

              {/* Table Rows */}
              {items.map((item, index) => (
                <Row key={index} style={tableRow}>
                  <Column style={colDescription}>
                    <Text style={itemDescription}>{item.description}</Text>
                  </Column>
                  <Column style={colQty}>
                    <Text style={itemText}>{item.quantity}</Text>
                  </Column>
                  <Column style={colPrice}>
                    <Text style={itemText}>{formatCurrency(item.unitPrice)}</Text>
                  </Column>
                  <Column style={colTotal}>
                    <Text style={itemText}>{formatCurrency(item.total)}</Text>
                  </Column>
                </Row>
              ))}
            </Section>

            <Hr style={divider} />

            {/* Totals */}
            <Section style={totalsSection}>
              <Row style={totalRow}>
                <Column style={totalLabelCol}>
                  <Text style={totalLabel}>Subtotal</Text>
                </Column>
                <Column style={totalValueCol}>
                  <Text style={totalValue}>{formatCurrency(totals.subtotal)}</Text>
                </Column>
              </Row>

              {totals.discount && (
                <Row style={totalRow}>
                  <Column style={totalLabelCol}>
                    <Text style={totalLabel}>
                      Discount {totals.discountCode && `(${totals.discountCode})`}
                    </Text>
                  </Column>
                  <Column style={totalValueCol}>
                    <Text style={{ ...totalValue, color: '#16a34a' }}>
                      -{formatCurrency(totals.discount)}
                    </Text>
                  </Column>
                </Row>
              )}

              <Row style={totalRow}>
                <Column style={totalLabelCol}>
                  <Text style={totalLabel}>Tax ({totals.taxRate}%)</Text>
                </Column>
                <Column style={totalValueCol}>
                  <Text style={totalValue}>{formatCurrency(totals.tax)}</Text>
                </Column>
              </Row>

              <Hr style={dividerSmall} />

              <Row style={totalRow}>
                <Column style={totalLabelCol}>
                  <Text style={grandTotalLabel}>
                    {type === 'refund' ? 'Refund Total' : 'Total'}
                  </Text>
                </Column>
                <Column style={totalValueCol}>
                  <Text style={grandTotalValue}>{formatCurrency(totals.total)}</Text>
                </Column>
              </Row>

              {type === 'invoice' && totals.amountPaid !== undefined && (
                <>
                  <Row style={totalRow}>
                    <Column style={totalLabelCol}>
                      <Text style={totalLabel}>Amount Paid</Text>
                    </Column>
                    <Column style={totalValueCol}>
                      <Text style={totalValue}>{formatCurrency(totals.amountPaid)}</Text>
                    </Column>
                  </Row>
                  <Row style={totalRow}>
                    <Column style={totalLabelCol}>
                      <Text style={amountDueLabel}>Amount Due</Text>
                    </Column>
                    <Column style={totalValueCol}>
                      <Text style={amountDueValue}>
                        {formatCurrency(totals.amountDue || totals.total - totals.amountPaid)}
                      </Text>
                    </Column>
                  </Row>
                </>
              )}
            </Section>

            <Hr style={divider} />

            {/* Payment Method & Billing Info */}
            <Row>
              {paymentMethod && type !== 'invoice' && (
                <Column style={infoColumn}>
                  <Text style={sectionTitle}>Payment Method</Text>
                  <Section style={infoBox}>
                    <Text style={infoText}>
                      {getPaymentIcon(paymentMethod.type)}{' '}
                      {paymentMethod.brand && `${paymentMethod.brand} `}
                      {paymentMethod.last4 && `•••• ${paymentMethod.last4}`}
                      {paymentMethod.email && paymentMethod.email}
                    </Text>
                  </Section>
                </Column>
              )}

              <Column style={infoColumn}>
                <Text style={sectionTitle}>
                  {type === 'invoice' ? 'Bill To' : 'Billing Address'}
                </Text>
                <Section style={infoBox}>
                  <Text style={infoText}>
                    {billingAddress.name}{'\n'}
                    {billingAddress.company && `${billingAddress.company}\n`}
                    {billingAddress.street}{'\n'}
                    {billingAddress.city}, {billingAddress.state} {billingAddress.zipCode}{'\n'}
                    {billingAddress.country}
                  </Text>
                </Section>
              </Column>
            </Row>

            {/* CTA Buttons */}
            <Section style={ctaContainer}>
              <Button style={ctaButton} href={invoiceUrl}>
                View {config.title} Online
              </Button>
              {pdfUrl && (
                <Link href={pdfUrl} style={pdfLink}>
                  Download PDF
                </Link>
              )}
            </Section>
          </Section>

          {/* Footer */}
          <Section style={footer}>
            {companyAddress && (
              <Text style={companyAddressText}>{companyAddress}</Text>
            )}
            <Text style={footerText}>
              Questions? Contact us at{' '}
              <Link href={`mailto:${supportEmail}`} style={footerLink}>
                {supportEmail}
              </Link>
            </Text>
            <Text style={footerText}>
              This email was sent to {customerEmail}
            </Text>
            <Text style={footerText}>
              © {new Date().getFullYear()} {companyName}. All rights reserved.
            </Text>
          </Section>
        </Container>
      </Body>
    </Html>
  )
}

// Styles
const main = {
  backgroundColor: '#f6f9fc',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Ubuntu, sans-serif',
}

const container = {
  backgroundColor: '#ffffff',
  margin: '0 auto',
  maxWidth: '600px',
}

const header = {
  padding: '32px 48px',
  borderBottom: '1px solid #e6ebf1',
}

const logoText = {
  fontSize: '24px',
  fontWeight: '700',
  color: '#1a1a1a',
  margin: '0',
}

const documentType = {
  fontSize: '14px',
  fontWeight: '700',
  letterSpacing: '1px',
  margin: '0',
}

const statusBanner = {
  padding: '24px',
  textAlign: 'center' as const,
}

const statusText = {
  fontSize: '16px',
  fontWeight: '600',
  margin: '0 0 8px',
}

const amountText = {
  fontSize: '32px',
  fontWeight: '700',
  margin: '0',
}

const content = {
  padding: '32px 48px',
}

const greeting = {
  color: '#1a1a1a',
  fontSize: '16px',
  margin: '0 0 16px',
}

const paragraph = {
  color: '#525f7f',
  fontSize: '14px',
  lineHeight: '22px',
  margin: '0 0 24px',
}

const detailsBox = {
  backgroundColor: '#f9fafb',
  borderRadius: '8px',
  padding: '16px',
}

const detailLabel = {
  color: '#6b7280',
  fontSize: '11px',
  textTransform: 'uppercase' as const,
  margin: '0 0 4px',
}

const detailValue = {
  color: '#1a1a1a',
  fontSize: '14px',
  fontWeight: '600',
  margin: '0',
}

const divider = {
  borderColor: '#e6ebf1',
  margin: '24px 0',
}

const dividerSmall = {
  borderColor: '#e6ebf1',
  margin: '12px 0',
}

const tableSection = {
  width: '100%',
}

const tableHeader = {
  backgroundColor: '#f9fafb',
  borderRadius: '4px',
  padding: '8px 0',
}

const tableHeaderText = {
  color: '#6b7280',
  fontSize: '11px',
  fontWeight: '600',
  textTransform: 'uppercase' as const,
  margin: '0',
}

const tableRow = {
  borderBottom: '1px solid #f3f4f6',
  padding: '12px 0',
}

const colDescription = { width: '50%' }
const colQty = { width: '15%', textAlign: 'center' as const }
const colPrice = { width: '17.5%', textAlign: 'right' as const }
const colTotal = { width: '17.5%', textAlign: 'right' as const }

const itemDescription = {
  color: '#1a1a1a',
  fontSize: '14px',
  margin: '0',
}

const itemText = {
  color: '#525f7f',
  fontSize: '14px',
  margin: '0',
}

const totalsSection = {
  marginLeft: 'auto',
  width: '250px',
}

const totalRow = {
  marginBottom: '8px',
}

const totalLabelCol = {
  textAlign: 'left' as const,
}

const totalValueCol = {
  textAlign: 'right' as const,
}

const totalLabel = {
  color: '#6b7280',
  fontSize: '14px',
  margin: '0',
}

const totalValue = {
  color: '#1a1a1a',
  fontSize: '14px',
  margin: '0',
}

const grandTotalLabel = {
  color: '#1a1a1a',
  fontSize: '16px',
  fontWeight: '700',
  margin: '0',
}

const grandTotalValue = {
  color: '#1a1a1a',
  fontSize: '18px',
  fontWeight: '700',
  margin: '0',
}

const amountDueLabel = {
  color: '#dc2626',
  fontSize: '14px',
  fontWeight: '600',
  margin: '0',
}

const amountDueValue = {
  color: '#dc2626',
  fontSize: '16px',
  fontWeight: '700',
  margin: '0',
}

const infoColumn = {
  width: '50%',
  verticalAlign: 'top' as const,
  paddingRight: '16px',
}

const sectionTitle = {
  color: '#1a1a1a',
  fontSize: '12px',
  fontWeight: '600',
  textTransform: 'uppercase' as const,
  margin: '0 0 8px',
}

const infoBox = {
  backgroundColor: '#f9fafb',
  borderRadius: '8px',
  padding: '12px',
}

const infoText = {
  color: '#374151',
  fontSize: '13px',
  lineHeight: '20px',
  margin: '0',
  whiteSpace: 'pre-line' as const,
}

const ctaContainer = {
  textAlign: 'center' as const,
  marginTop: '32px',
}

const ctaButton = {
  backgroundColor: '#1a1a1a',
  borderRadius: '8px',
  color: '#ffffff',
  fontSize: '14px',
  fontWeight: '600',
  padding: '12px 24px',
  textDecoration: 'none',
}

const pdfLink = {
  color: '#556cd6',
  display: 'block',
  fontSize: '14px',
  marginTop: '12px',
  textDecoration: 'underline',
}

const footer = {
  padding: '32px 48px',
  borderTop: '1px solid #e6ebf1',
  textAlign: 'center' as const,
}

const companyAddressText = {
  color: '#6b7280',
  fontSize: '12px',
  margin: '0 0 16px',
}

const footerText = {
  color: '#8898aa',
  fontSize: '12px',
  margin: '0 0 8px',
}

const footerLink = {
  color: '#556cd6',
  textDecoration: 'underline',
}

export default InvoiceReceiptEmail
