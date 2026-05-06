"""
CRAFT Pricing & Payment System
Revenue generation through transparent, value-based pricing.

Every dollar earned funds mental health support for people in crisis.
Price fairly, deliver generously, build sustainably.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class PricingTier:
    """Video production pricing tier"""
    name: str
    base_price: float
    description: str
    features: List[str]
    scene_count: int
    resolution: str
    delivery_days: int
    revision_rounds: int
    aspect_ratios: List[str]
    includes_music_rights_consultation: bool = False
    includes_social_cutdowns: bool = False
    priority_support: bool = False


class CRAFTPricingEngine:
    """
    Intelligent pricing system that balances profitability with accessibility.
    """

    # Core pricing tiers
    TIERS = {
        'basic': PricingTier(
            name='Basic',
            base_price=297.0,
            description='Perfect for emerging artists and single releases',
            features=[
                '8 unique AI-generated scenes',
                '1080p HD resolution',
                'Professional audio sync',
                'Color grading and transitions',
                'Standard delivery (7 business days)',
                '1 round of revisions',
                'YouTube optimization'
            ],
            scene_count=8,
            resolution='1080p',
            delivery_days=7,
            revision_rounds=1,
            aspect_ratios=['16:9'],
        ),
        'standard': PricingTier(
            name='Standard',
            base_price=697.0,
            description='Most popular - Professional quality for serious artists',
            features=[
                '15 unique AI-generated scenes',
                '4K Ultra HD resolution',
                'Advanced motion graphics',
                'Professional audio sync and color grading',
                'Priority delivery (5 business days)',
                '2 rounds of revisions',
                'Multi-platform optimization',
                'Instagram/TikTok cut-downs included',
                'Music rights consultation'
            ],
            scene_count=15,
            resolution='4K',
            delivery_days=5,
            revision_rounds=2,
            aspect_ratios=['16:9', '9:16', '1:1'],
            includes_music_rights_consultation=True,
            includes_social_cutdowns=True,
        ),
        'premium': PricingTier(
            name='Premium',
            base_price=1997.0,
            description='Industry-grade production for professional releases',
            features=[
                '25+ unique AI-generated scenes',
                '4K+ Cinema-quality resolution',
                'Cinematic VFX and advanced motion graphics',
                'Professional color grading and effects',
                'Express delivery (3 business days)',
                'Unlimited revisions (30 days)',
                'All aspect ratios and platform optimizations',
                'Social media cut-downs (3 versions)',
                'Dedicated project manager',
                'Music rights consultation',
                'Distribution strategy session',
                'Behind-the-scenes content'
            ],
            scene_count=25,
            resolution='4K+',
            delivery_days=3,
            revision_rounds=999,  # Unlimited
            aspect_ratios=['16:9', '9:16', '1:1', '4:5', 'custom'],
            includes_music_rights_consultation=True,
            includes_social_cutdowns=True,
            priority_support=True,
        )
    }

    # Add-on services
    ADD_ONS = {
        'rush_24hr': {
            'name': '24-Hour Rush Delivery',
            'price': 0.50,  # 50% of base price
            'description': 'Expedited 24-hour turnaround'
        },
        'rush_48hr': {
            'name': '48-Hour Rush Delivery',
            'price': 0.30,  # 30% of base price
            'description': 'Expedited 48-hour turnaround'
        },
        'extra_revision': {
            'name': 'Additional Revision Round',
            'price': 97.0,
            'description': 'Extra round of revisions beyond package limit'
        },
        'extra_cutdown': {
            'name': 'Additional Social Cut-Down',
            'price': 47.0,
            'description': 'Additional platform-optimized version'
        },
        'artist_footage_integration': {
            'name': 'Artist Footage Integration',
            'price': 197.0,
            'description': 'Integrate client-provided footage into AI-generated scenes'
        },
        'custom_vfx': {
            'name': 'Custom VFX Element',
            'price': 297.0,
            'description': 'Bespoke visual effect or motion graphic element'
        },
        'extended_length': {
            'name': 'Extended Length Video',
            'price': 0.20,  # 20% of base per extra minute
            'description': 'For songs over 4 minutes (per additional minute)'
        },
        'lyrics_overlay': {
            'name': 'Animated Lyrics Overlay',
            'price': 147.0,
            'description': 'Professional animated lyrics throughout video'
        },
        'distribution_package': {
            'name': 'Distribution Strategy Package',
            'price': 497.0,
            'description': 'Complete distribution strategy, metadata optimization, and promotional assets'
        }
    }

    # Volume discounts
    VOLUME_DISCOUNTS = {
        3: 0.10,   # 10% off for 3+ videos
        5: 0.15,   # 15% off for 5+ videos
        10: 0.20,  # 20% off for 10+ videos
    }

    # Referral bonuses
    REFERRAL_DISCOUNT = 0.15  # 15% off for referred clients

    def __init__(self):
        pass

    def calculate_project_price(self,
                               tier: str,
                               add_ons: List[str] = None,
                               song_duration_minutes: float = 3.5,
                               volume_count: int = 1,
                               has_referral: bool = False) -> Dict:
        """
        Calculate complete project pricing with all modifiers.
        """
        if tier not in self.TIERS:
            raise ValueError(f"Invalid tier: {tier}")

        pricing_tier = self.TIERS[tier]
        base_price = pricing_tier.base_price

        # Start with base price
        subtotal = base_price
        breakdown = {
            'tier': tier,
            'base_price': base_price,
            'line_items': [
                {
                    'description': f'{pricing_tier.name} Package',
                    'amount': base_price
                }
            ]
        }

        # Add-ons
        addon_total = 0
        if add_ons:
            for addon_key in add_ons:
                if addon_key in self.ADD_ONS:
                    addon = self.ADD_ONS[addon_key]

                    # Calculate addon price
                    if isinstance(addon['price'], float) and addon['price'] < 1:
                        # Percentage-based addon
                        addon_price = base_price * addon['price']
                    else:
                        addon_price = addon['price']

                    # Extended length special calculation
                    if addon_key == 'extended_length' and song_duration_minutes > 4:
                        extra_minutes = song_duration_minutes - 4
                        addon_price = base_price * addon['price'] * extra_minutes

                    addon_total += addon_price
                    breakdown['line_items'].append({
                        'description': addon['name'],
                        'amount': addon_price
                    })

        subtotal += addon_total

        # Volume discount
        volume_discount_amount = 0
        volume_discount_percent = 0
        if volume_count > 1:
            for count, discount in sorted(self.VOLUME_DISCOUNTS.items(), reverse=True):
                if volume_count >= count:
                    volume_discount_percent = discount
                    volume_discount_amount = subtotal * discount
                    breakdown['line_items'].append({
                        'description': f'Volume Discount ({int(discount*100)}% off for {volume_count} videos)',
                        'amount': -volume_discount_amount
                    })
                    break

        # Referral discount
        referral_discount_amount = 0
        if has_referral:
            referral_discount_amount = subtotal * self.REFERRAL_DISCOUNT
            breakdown['line_items'].append({
                'description': f'Referral Discount (15% off)',
                'amount': -referral_discount_amount
            })

        # Calculate final total
        total_discounts = volume_discount_amount + referral_discount_amount
        final_total = subtotal - total_discounts

        breakdown['subtotal'] = subtotal
        breakdown['total_discounts'] = total_discounts
        breakdown['final_total'] = final_total

        # Revenue impact
        breakdown['revenue_impact'] = {
            'gross_revenue': final_total,
            'funds_mental_health_support': True,
            'estimated_people_helped': self._estimate_people_helped(final_total)
        }

        return breakdown

    def _estimate_people_helped(self, revenue: float) -> int:
        """
        Estimate how many people this revenue can support.
        Assuming $50-100 per person for crisis intervention.
        """
        return int(revenue / 75)

    def generate_quote(self, pricing_breakdown: Dict, client_name: str = "Valued Client") -> str:
        """
        Generate a professional quote document.
        """
        tier = pricing_breakdown['tier'].upper()
        tier_info = self.TIERS[pricing_breakdown['tier']]

        quote = f"""
{'='*70}
CRAFT VIDEO PRODUCTION - PROJECT QUOTE
{'='*70}

Client: {client_name}
Date: {datetime.now().strftime('%B %d, %Y')}
Quote Valid Until: {(datetime.now() + timedelta(days=14)).strftime('%B %d, %Y')}

{'='*70}
PACKAGE: {tier_info.name.upper()}
{'='*70}

{tier_info.description}

INCLUDES:
"""
        for feature in tier_info.features:
            quote += f"  - {feature}\n"

        quote += f"\n{'='*70}\nPRICING BREAKDOWN\n{'='*70}\n\n"

        for item in pricing_breakdown['line_items']:
            amount_str = f"${item['amount']:,.2f}" if item['amount'] >= 0 else f"-${abs(item['amount']):,.2f}"
            quote += f"{item['description']:<50} {amount_str:>15}\n"

        quote += f"\n{'-'*70}\n"
        quote += f"{'Subtotal':<50} ${pricing_breakdown['subtotal']:>14,.2f}\n"

        if pricing_breakdown['total_discounts'] > 0:
            quote += f"{'Total Savings':<50} -${pricing_breakdown['total_discounts']:>13,.2f}\n"
            quote += f"{'-'*70}\n"

        quote += f"{'TOTAL':<50} ${pricing_breakdown['final_total']:>14,.2f}\n"
        quote += f"{'='*70}\n\n"

        # Impact statement
        people_helped = pricing_breakdown['revenue_impact']['estimated_people_helped']
        quote += f"""
YOUR IMPACT:
This project generates ${pricing_breakdown['final_total']:,.2f} in revenue, which
funds mental health crisis support for approximately {people_helped} people.

Your video doesn't just showcase your art - it helps heal.

{'='*70}
PAYMENT TERMS
{'='*70}

  - 50% deposit to begin production
  - 50% due upon delivery of final video
  - Payment accepted via: Credit Card, PayPal, Bank Transfer
  - All prices in USD

{'='*70}
WHAT HAPPENS NEXT
{'='*70}

1. Accept this quote by replying or clicking the acceptance link
2. Pay 50% deposit to secure your production slot
3. Submit your project intake form with creative details
4. Receive creative treatment within 24 hours
5. Production begins upon treatment approval
6. Final delivery in {tier_info.delivery_days} business days

{'='*70}
QUESTIONS?
{'='*70}

Email: support@eversound.com
Phone: [PHONE NUMBER]
Web: www.eversound.com/craft

We're excited to bring your artistic vision to life.

With creative passion,
CRAFT Video Production Team
Eversound Family

---
"Creating revenue that heals"
"""

        return quote

    def create_payment_link(self, pricing_breakdown: Dict, client_email: str, project_id: str) -> Dict:
        """
        Generate payment link (would integrate with Stripe, PayPal, etc.)
        """
        total = pricing_breakdown['final_total']
        deposit = total * 0.5

        # In production, this would create actual payment links
        payment_info = {
            'project_id': project_id,
            'client_email': client_email,
            'total_amount': total,
            'deposit_amount': deposit,
            'balance_amount': total - deposit,
            'payment_links': {
                'stripe_deposit': f"https://pay.stripe.com/deposit/{project_id}",
                'stripe_balance': f"https://pay.stripe.com/balance/{project_id}",
                'paypal_deposit': f"https://paypal.com/invoice/{project_id}/deposit",
                'paypal_balance': f"https://paypal.com/invoice/{project_id}/balance"
            },
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }

        return payment_info

    def track_payment(self, project_id: str, amount: float, payment_method: str) -> Dict:
        """
        Track payment received (would integrate with payment processor webhooks)
        """
        payment_record = {
            'project_id': project_id,
            'amount': amount,
            'payment_method': payment_method,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'transaction_id': hashlib.md5(f"{project_id}{amount}{datetime.now()}".encode()).hexdigest()[:16]
        }

        print(f"\n{'='*70}")
        print(f"PAYMENT RECEIVED")
        print(f"{'='*70}")
        print(f"Project ID: {project_id}")
        print(f"Amount: ${amount:,.2f}")
        print(f"Method: {payment_method}")
        print(f"Transaction: {payment_record['transaction_id']}")
        print(f"{'='*70}\n")

        # Notify Unc about revenue
        try:
            from notify_unc import send_notification_to_unc

            send_notification_to_unc(
                from_agent="CRAFT",
                subject=f"Payment Received: ${amount:,.2f}",
                message=f"""
PAYMENT PROCESSED

Project: {project_id}
Amount: ${amount:,.2f}
Method: {payment_method}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Transaction: {payment_record['transaction_id']}

This revenue funds mental health support.

CRAFT Revenue System
""",
                priority="normal"
            )
        except:
            pass

        return payment_record

    def generate_invoice(self, pricing_breakdown: Dict, client_info: Dict, project_info: Dict) -> str:
        """
        Generate professional invoice.
        """
        invoice_number = f"CRAFT-{datetime.now().strftime('%Y%m%d')}-{project_info['project_id'][:8]}"

        invoice = f"""
{'='*70}
                        INVOICE
{'='*70}

Invoice #: {invoice_number}
Date: {datetime.now().strftime('%B %d, %Y')}
Due Date: {(datetime.now() + timedelta(days=7)).strftime('%B %d, %Y')}

{'='*70}
FROM:
{'='*70}

CRAFT Video Production
Eversound Family
[ADDRESS]
[CITY, STATE ZIP]
[PHONE]
support@eversound.com

{'='*70}
BILL TO:
{'='*70}

{client_info['name']}
{client_info.get('company', '')}
{client_info['email']}
{client_info.get('phone', '')}

{'='*70}
PROJECT DETAILS
{'='*70}

Project ID: {project_info['project_id']}
Song Title: {project_info['song_title']}
Artist: {project_info['artist_name']}
Package: {pricing_breakdown['tier'].upper()}

{'='*70}
SERVICES
{'='*70}

"""
        for item in pricing_breakdown['line_items']:
            amount_str = f"${item['amount']:,.2f}" if item['amount'] >= 0 else f"-${abs(item['amount']):,.2f}"
            invoice += f"{item['description']:<50} {amount_str:>15}\n"

        invoice += f"\n{'-'*70}\n"
        invoice += f"{'Subtotal':<50} ${pricing_breakdown['subtotal']:>14,.2f}\n"

        if pricing_breakdown['total_discounts'] > 0:
            invoice += f"{'Discounts':<50} -${pricing_breakdown['total_discounts']:>13,.2f}\n"

        invoice += f"{'-'*70}\n"
        invoice += f"{'TOTAL DUE':<50} ${pricing_breakdown['final_total']:>14,.2f}\n"
        invoice += f"{'='*70}\n\n"

        invoice += """
PAYMENT METHODS:

  Credit Card / Debit Card
  PayPal
  Bank Transfer (ACH)
  Wire Transfer

PAYMENT INSTRUCTIONS:

  Pay online: [PAYMENT LINK]
  Or send payment to: payments@eversound.com

{'='*70}
NOTES
{'='*70}

Thank you for choosing CRAFT Video Production. Your project helps
fund mental health crisis support for people in need.

Your art creates healing.

{'='*70}
"""

        return invoice


def demo_pricing_system():
    """
    Demonstrate the pricing and payment system.
    """
    print("\n" + "="*70)
    print("CRAFT PRICING & PAYMENT SYSTEM - DEMONSTRATION")
    print("="*70 + "\n")

    pricing_engine = CRAFTPricingEngine()

    # Example 1: Basic package
    print("\n--- EXAMPLE 1: Basic Package ---\n")
    basic_pricing = pricing_engine.calculate_project_price(
        tier='basic',
        song_duration_minutes=3.5
    )

    quote1 = pricing_engine.generate_quote(basic_pricing, "Emerging Artist")
    print(quote1)

    # Example 2: Standard package with add-ons
    print("\n--- EXAMPLE 2: Standard Package with Rush & Lyrics ---\n")
    standard_pricing = pricing_engine.calculate_project_price(
        tier='standard',
        add_ons=['rush_48hr', 'lyrics_overlay'],
        song_duration_minutes=4.2,
        has_referral=True
    )

    quote2 = pricing_engine.generate_quote(standard_pricing, "Pro Artist (Referred)")
    print(quote2)

    # Example 3: Premium package with volume discount
    print("\n--- EXAMPLE 3: Premium Package - Album Deal (5 videos) ---\n")
    premium_pricing = pricing_engine.calculate_project_price(
        tier='premium',
        add_ons=['distribution_package', 'custom_vfx'],
        song_duration_minutes=4.5,
        volume_count=5
    )

    quote3 = pricing_engine.generate_quote(premium_pricing, "Major Label Artist")
    print(quote3)

    # Show pricing comparison
    print("\n" + "="*70)
    print("PRICING TIERS COMPARISON")
    print("="*70 + "\n")

    for tier_key, tier_info in pricing_engine.TIERS.items():
        print(f"{tier_info.name.upper()}: ${tier_info.base_price:,.2f}")
        print(f"  Scenes: {tier_info.scene_count}")
        print(f"  Resolution: {tier_info.resolution}")
        print(f"  Delivery: {tier_info.delivery_days} days")
        print(f"  Revisions: {tier_info.revision_rounds}")
        print()

    print("="*70 + "\n")


if __name__ == "__main__":
    demo_pricing_system()
