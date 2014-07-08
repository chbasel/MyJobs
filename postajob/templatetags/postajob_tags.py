import bleach

from django.core.urlresolvers import resolve
from django.template import Library
from django.utils.text import slugify
from django.utils.safestring import mark_safe

from postajob.models import PurchasedJob, PurchasedProduct

register = Library()


@register.simple_tag
def get_job_links(job, max_sites=3):
    sites = job.on_sites()
    domains = [site.domain for site in sites]

    location = u'{city}, {state}'.format(city=job.city, state=job.state_short)
    loc_slug = bleach.clean(slugify(location))
    title_slug = bleach.clean(slugify(job.title))

    base_url = 'http://{domain}/{loc_slug}/{title_slug}/{guid}/job/'
    href_tag = '<a href="{url}">{domain}</a>'
    urls = []
    for domain in domains:
        job_url = base_url.format(domain=domain, loc_slug=loc_slug,
                                  title_slug=title_slug, guid=job.guid)

        urls.append(href_tag.format(url=job_url, domain=domain))
    url_html = mark_safe("<br/>".join(urls[:max_sites]))
    if max_sites and len(urls) > max_sites:
        url_html = mark_safe("%s <br/>..." % url_html)
    return url_html


@register.assignment_tag
def get_jobs(purchased_product):
    return PurchasedJob.objects.filter(purchased_product=purchased_product)


@register.simple_tag(takes_context=True)
def get_form_action(context):
    current_url_name = resolve(context['request'].path).url_name
    if context.get('item') and context['item'].pk:
        return 'Edit'
    elif current_url_name == 'purchasedproduct_add':
        return 'Purchase'
    return 'Add'


@register.assignment_tag
def get_purchase_total(purchases):
    return sum(purchase.purchase_amount for purchase in purchases)


@register.simple_tag
def get_redeemer(offline_purchase):
    # This is only set if a user has redeemed the purchase.
    if offline_purchase.redeemed_by:
        return offline_purchase.redeemed_by.company.name
    # Otherwise attempt to get the name from a Product created from the
    # OfflinePurchase.
    else:
        products = PurchasedProduct.objects.filter(
            offline_purchase=offline_purchase)
        if products:
            return products[0].owner

    # Otherwise the product hasn't been redeemed yet, and therefore there
    # is no redeemer.
    return ''


@register.simple_tag
def get_product_names(offline_purchase):
    products = offline_purchase.products.all()
    names = [product.name for product in products]
    return ", ".join(names)
