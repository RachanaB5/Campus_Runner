/**
 * Order Notification Email Template
 * Usage: Order confirmation, shipping updates, delivery notifications
 * 
 * Dependencies: @react-email/components
 * 
 * Props:
 * - customerName: string - Customer's display name
 * - orderId: string - Order reference number
 * - orderDate: string - When the order was placed
 * - notificationType: 'confirmed' | 'shipped' | 'out-for-delivery' | 'delivered'
 * - items: Array<{name, quantity, price, image}> - Order items
 * - shippingAddress: object - Delivery address
 * - trackingNumber: string - Shipping tracking number
 * - trackingUrl: string - URL to track shipment
 * - estimatedDelivery: string - Expected delivery date
 * - orderTotal: object - Price breakdown
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

interface OrderItem {
  name: string
  quantity: number
  price: number
  image?: string
  variant?: string
}

interface ShippingAddress {
  name: string
  street: string
  city: string
  state: string
  zipCode: string
  country: string
}

interface OrderTotal {
  subtotal: number
  shipping: number
  tax: number
  discount?: number
  total: number
}

interface OrderNotificationEmailProps {
  customerName: string
  orderId: string
  orderDate: string
  notificationType: 'confirmed' | 'shipped' | 'out-for-delivery' | 'delivered'
  items: OrderItem[]
  shippingAddress: ShippingAddress
  trackingNumber?: string
  trackingUrl?: string
  estimatedDelivery?: string
  orderTotal: OrderTotal
  companyName: string
  companyLogo?: string
  supportEmail: string
  orderUrl: string
}

const statusConfig = {
  confirmed: {
    title: 'Order Confirmed',
    icon: '✓',
    color: '#16a34a',
    bgColor: '#f0fdf4',
    message: 'Thank you for your order! We\'re preparing it now.',
  },
  shipped: {
    title: 'Order Shipped',
    icon: '📦',
    color: '#2563eb',
    bgColor: '#eff6ff',
    message: 'Great news! Your order is on its way.',
  },
  'out-for-delivery': {
    title: 'Out for Delivery',
    icon: '🚚',
    color: '#d97706',
    bgColor: '#fffbeb',
    message: 'Your package is out for delivery today!',
  },
  delivered: {
    title: 'Order Delivered',
    icon: '🎉',
    color: '#16a34a',
    bgColor: '#f0fdf4',
    message: 'Your order has been delivered. Enjoy!',
  },
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount)
}

export function OrderNotificationEmail({
  customerName = 'Customer',
  orderId = 'ORD-12345',
  orderDate = new Date().toLocaleDateString(),
  notificationType = 'confirmed',
  items = [
    { name: 'Sample Product', quantity: 1, price: 99.99 },
  ],
  shippingAddress = {
    name: 'John Doe',
    street: '123 Main St',
    city: 'New York',
    state: 'NY',
    zipCode: '10001',
    country: 'United States',
  },
  trackingNumber,
  trackingUrl,
  estimatedDelivery,
  orderTotal = {
    subtotal: 99.99,
    shipping: 5.99,
    tax: 8.50,
    total: 114.48,
  },
  companyName = 'Your Store',
  companyLogo,
  supportEmail = 'support@yourstore.com',
  orderUrl = 'https://yourstore.com/orders/12345',
}: OrderNotificationEmailProps) {
  const status = statusConfig[notificationType]

  return (
    <Html>
      <Head />
      <Preview>{status.title} - Order #{orderId}</Preview>
      <Body style={main}>
        <Container style={container}>
          {/* Header */}
          <Section style={header}>
            {companyLogo ? (
              <Img src={companyLogo} width="120" height="40" alt={companyName} />
            ) : (
              <Text style={logoText}>{companyName}</Text>
            )}
          </Section>

          {/* Status Banner */}
          <Section style={{ ...statusBanner, backgroundColor: status.bgColor }}>
            <Text style={{ ...statusIcon, color: status.color }}>{status.icon}</Text>
            <Heading style={{ ...statusTitle, color: status.color }}>
              {status.title}
            </Heading>
            <Text style={{ ...statusMessage, color: status.color }}>
              {status.message}
            </Text>
          </Section>

          {/* Main Content */}
          <Section style={content}>
            <Text style={paragraph}>Hi {customerName},</Text>

            {/* Order Info */}
            <Section style={orderInfoBox}>
              <Row>
                <Column>
                  <Text style={orderInfoLabel}>Order Number</Text>
                  <Text style={orderInfoValue}>{orderId}</Text>
                </Column>
                <Column>
                  <Text style={orderInfoLabel}>Order Date</Text>
                  <Text style={orderInfoValue}>{orderDate}</Text>
                </Column>
                {estimatedDelivery && (
                  <Column>
                    <Text style={orderInfoLabel}>Est. Delivery</Text>
                    <Text style={orderInfoValue}>{estimatedDelivery}</Text>
                  </Column>
                )}
              </Row>
            </Section>

            {/* Tracking Info (if shipped) */}
            {trackingNumber && (
              <Section style={trackingBox}>
                <Text style={trackingLabel}>Tracking Number</Text>
                <Text style={trackingNumber as unknown as React.CSSProperties}>
                  {trackingNumber}
                </Text>
                {trackingUrl && (
                  <Button style={trackButton} href={trackingUrl}>
                    Track Package
                  </Button>
                )}
              </Section>
            )}

            <Hr style={divider} />

            {/* Order Items */}
            <Text style={sectionTitle}>Order Summary</Text>
            {items.map((item, index) => (
              <Section key={index} style={itemRow}>
                <Row>
                  <Column style={itemImageCol}>
                    {item.image ? (
                      <Img
                        src={item.image}
                        width="64"
                        height="64"
                        alt={item.name}
                        style={itemImage}
                      />
                    ) : (
                      <Section style={itemImagePlaceholder}>
                        <Text style={itemImagePlaceholderText}>📦</Text>
                      </Section>
                    )}
                  </Column>
                  <Column style={itemDetailsCol}>
                    <Text style={itemName}>{item.name}</Text>
                    {item.variant && (
                      <Text style={itemVariant}>{item.variant}</Text>
                    )}
                    <Text style={itemQuantity}>Qty: {item.quantity}</Text>
                  </Column>
                  <Column style={itemPriceCol}>
                    <Text style={itemPrice}>{formatCurrency(item.price)}</Text>
                  </Column>
                </Row>
              </Section>
            ))}

            <Hr style={divider} />

            {/* Price Breakdown */}
            <Section style={priceBreakdown}>
              <Row style={priceRow}>
                <Column><Text style={priceLabel}>Subtotal</Text></Column>
                <Column><Text style={priceValue}>{formatCurrency(orderTotal.subtotal)}</Text></Column>
              </Row>
              <Row style={priceRow}>
                <Column><Text style={priceLabel}>Shipping</Text></Column>
                <Column>
                  <Text style={priceValue}>
                    {orderTotal.shipping === 0 ? 'FREE' : formatCurrency(orderTotal.shipping)}
                  </Text>
                </Column>
              </Row>
              <Row style={priceRow}>
                <Column><Text style={priceLabel}>Tax</Text></Column>
                <Column><Text style={priceValue}>{formatCurrency(orderTotal.tax)}</Text></Column>
              </Row>
              {orderTotal.discount && (
                <Row style={priceRow}>
                  <Column><Text style={priceLabel}>Discount</Text></Column>
                  <Column>
                    <Text style={{ ...priceValue, color: '#16a34a' }}>
                      -{formatCurrency(orderTotal.discount)}
                    </Text>
                  </Column>
                </Row>
              )}
              <Hr style={dividerSmall} />
              <Row style={priceRow}>
                <Column><Text style={totalLabel}>Total</Text></Column>
                <Column><Text style={totalValue}>{formatCurrency(orderTotal.total)}</Text></Column>
              </Row>
            </Section>

            <Hr style={divider} />

            {/* Shipping Address */}
            <Text style={sectionTitle}>Shipping Address</Text>
            <Section style={addressBox}>
              <Text style={addressText}>
                {shippingAddress.name}{'\n'}
                {shippingAddress.street}{'\n'}
                {shippingAddress.city}, {shippingAddress.state} {shippingAddress.zipCode}{'\n'}
                {shippingAddress.country}
              </Text>
            </Section>

            {/* CTA */}
            <Section style={ctaContainer}>
              <Button style={ctaButton} href={orderUrl}>
                View Order Details
              </Button>
            </Section>
          </Section>

          {/* Footer */}
          <Section style={footer}>
            <Text style={footerText}>
              Questions about your order? Contact us at{' '}
              <Link href={`mailto:${supportEmail}`} style={footerLink}>
                {supportEmail}
              </Link>
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

const statusBanner = {
  padding: '32px',
  textAlign: 'center' as const,
}

const statusIcon = {
  fontSize: '48px',
  margin: '0 0 8px',
}

const statusTitle = {
  fontSize: '24px',
  fontWeight: '700',
  margin: '0 0 8px',
}

const statusMessage = {
  fontSize: '16px',
  margin: '0',
}

const content = {
  padding: '32px 48px',
}

const paragraph = {
  color: '#525f7f',
  fontSize: '16px',
  lineHeight: '24px',
  margin: '0 0 24px',
}

const orderInfoBox = {
  backgroundColor: '#f9fafb',
  borderRadius: '8px',
  padding: '16px',
  marginBottom: '24px',
}

const orderInfoLabel = {
  color: '#6b7280',
  fontSize: '12px',
  textTransform: 'uppercase' as const,
  margin: '0 0 4px',
}

const orderInfoValue = {
  color: '#1a1a1a',
  fontSize: '14px',
  fontWeight: '600',
  margin: '0',
}

const trackingBox = {
  backgroundColor: '#eff6ff',
  borderRadius: '8px',
  padding: '20px',
  textAlign: 'center' as const,
  marginBottom: '24px',
}

const trackingLabel = {
  color: '#1e40af',
  fontSize: '12px',
  textTransform: 'uppercase' as const,
  margin: '0 0 8px',
}

const trackButton = {
  backgroundColor: '#2563eb',
  borderRadius: '6px',
  color: '#ffffff',
  fontSize: '14px',
  fontWeight: '600',
  padding: '10px 20px',
  textDecoration: 'none',
  marginTop: '12px',
}

const divider = {
  borderColor: '#e6ebf1',
  margin: '24px 0',
}

const dividerSmall = {
  borderColor: '#e6ebf1',
  margin: '12px 0',
}

const sectionTitle = {
  color: '#1a1a1a',
  fontSize: '16px',
  fontWeight: '600',
  margin: '0 0 16px',
}

const itemRow = {
  marginBottom: '16px',
}

const itemImageCol = {
  width: '80px',
  verticalAlign: 'top' as const,
}

const itemImage = {
  borderRadius: '8px',
  objectFit: 'cover' as const,
}

const itemImagePlaceholder = {
  width: '64px',
  height: '64px',
  backgroundColor: '#f3f4f6',
  borderRadius: '8px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}

const itemImagePlaceholderText = {
  fontSize: '24px',
  margin: '0',
  textAlign: 'center' as const,
  lineHeight: '64px',
}

const itemDetailsCol = {
  verticalAlign: 'top' as const,
  paddingLeft: '12px',
}

const itemName = {
  color: '#1a1a1a',
  fontSize: '14px',
  fontWeight: '600',
  margin: '0 0 4px',
}

const itemVariant = {
  color: '#6b7280',
  fontSize: '13px',
  margin: '0 0 4px',
}

const itemQuantity = {
  color: '#6b7280',
  fontSize: '13px',
  margin: '0',
}

const itemPriceCol = {
  verticalAlign: 'top' as const,
  textAlign: 'right' as const,
}

const itemPrice = {
  color: '#1a1a1a',
  fontSize: '14px',
  fontWeight: '600',
  margin: '0',
}

const priceBreakdown = {
  marginBottom: '24px',
}

const priceRow = {
  marginBottom: '8px',
}

const priceLabel = {
  color: '#6b7280',
  fontSize: '14px',
  margin: '0',
}

const priceValue = {
  color: '#1a1a1a',
  fontSize: '14px',
  margin: '0',
  textAlign: 'right' as const,
}

const totalLabel = {
  color: '#1a1a1a',
  fontSize: '16px',
  fontWeight: '700',
  margin: '0',
}

const totalValue = {
  color: '#1a1a1a',
  fontSize: '18px',
  fontWeight: '700',
  margin: '0',
  textAlign: 'right' as const,
}

const addressBox = {
  backgroundColor: '#f9fafb',
  borderRadius: '8px',
  padding: '16px',
  marginBottom: '24px',
}

const addressText = {
  color: '#374151',
  fontSize: '14px',
  lineHeight: '22px',
  margin: '0',
  whiteSpace: 'pre-line' as const,
}

const ctaContainer = {
  textAlign: 'center' as const,
}

const ctaButton = {
  backgroundColor: '#1a1a1a',
  borderRadius: '8px',
  color: '#ffffff',
  fontSize: '16px',
  fontWeight: '600',
  padding: '14px 32px',
  textDecoration: 'none',
}

const footer = {
  padding: '32px 48px',
  borderTop: '1px solid #e6ebf1',
  textAlign: 'center' as const,
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

export default OrderNotificationEmail
