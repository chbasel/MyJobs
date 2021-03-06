from datetime import date
from fsm.views import FSMView
import json

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import Http404, reverse, reverse_lazy, resolve
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from myjobs.models import User
from postajob.location_data import state_list

from seo.models import SeoSite
from myjobs.decorators import user_is_allowed, MissingActivity
from postajob.forms import (CompanyProfileForm, JobForm, OfflinePurchaseForm,
                            OfflinePurchaseRedemptionForm, ProductForm,
                            ProductGroupingForm, PurchasedJobForm,
                            PurchasedProductForm,
                            PurchasedProductNoPurchaseForm,
                            JobLocationFormSet, MarketPlaceEnableForm)
from postajob.models import (CompanyProfile, Invoice, Job, OfflinePurchase,
                             Product, ProductGrouping, PurchasedJob,
                             PurchasedProduct, Request, JobLocation)
from postajob.helpers import can_modify, enable_posting, enable_marketplace
from universal.helpers import (get_company, get_object_or_none,
                               get_company_or_404, at_least_one)
from universal.views import RequestFormViewBase
from universal.decorators import restrict_to_staff
from myjobs.decorators import requires


@restrict_to_staff()
def enable_feature(request, feature):
    ctx = {'feature': feature}
    if request.method == "POST":
        form = MarketPlaceEnableForm(request.POST)

        if form.is_valid():
            company = form.cleaned_data['company']
            site = form.cleaned_data['site']
            if feature == 'Posting':
                enable_posting(company, site)
            elif feature == 'MarketPlace':
                enable_marketplace(company, site)
            ctx['message'] = 'Success'
    else:
        form = MarketPlaceEnableForm()
    ctx['form'] = form

    return render_to_response(
        'postajob/enable_feature.html', ctx, RequestContext(request))


@user_is_allowed()
@requires('read job')
def jobs_overview(request):
    sites = settings.SITE.postajob_site_list()
    jobs = Job.objects.filter_by_sites(sites)
    company = settings.SITE.canonical_company
    data = {
        'company' : company,
        'jobs': jobs.filter(owner=company, purchasedjob__isnull=True),
    }
    return render_to_response('postajob/jobs_overview.html', data,
                              RequestContext(request))


@user_is_allowed()
@requires('read purchased product')
def view_job(request, purchased_product, pk, admin):
    http404_view = 'postajob.views.view_job'
    company = get_company_or_404(request)
    purchased_product = PurchasedProduct.objects.get(pk=purchased_product)
    if admin and purchased_product.product.owner != company:
        raise Http404("{view}: Current company and product owner do not "
                      "match".format(view=http404_view))
    elif not admin and purchased_product.owner != company:
        raise Http404("{view}: Current company and purchased product owner do "
                      "not match".format(view=http404_view))
    data = {
        'admin': admin,
        'company': company,
        'purchased_product': purchased_product,
        'job': PurchasedJob.objects.get(pk=pk)
    }
    return render_to_response('postajob/view_job.html',
                              data, RequestContext(request))

@requires('read invoice')
def view_invoice(request, purchased_product):
    company = get_company_or_404(request)
    kwargs = {
        'pk': purchased_product,
    }
    if 'posting/admin' in request.get_full_path():
        kwargs['product__owner'] = company
    else:
        kwargs['owner'] = company
    product = get_object_or_404(PurchasedProduct, **kwargs)
    invoice = product.invoice
    data = {
        'company': company,
        'purchased_product': product,
        'invoice': invoice,
        'purchases': invoice.invoiced_products.all()
    }
    # m is used to render success message. Also, 'm' for shorter url query set.
    if 'm' in request.GET:
        data.update({'alert': 'success',
                     'alert_message': '<b>Success!</b>  You should receive '
                                      'this invoice shortly.'
                     })
    return render_to_response('postajob/view_invoice.html',
                              data, RequestContext(request))


@user_is_allowed()
@requires("read purchased product")
def purchasedproducts_overview(request):
    company = get_company_or_404(request)
    sites = settings.SITE.postajob_site_list()
    products = PurchasedProduct.objects.filter_by_sites(sites)
    jobs = PurchasedJob.objects.filter_by_sites(sites)
    products = products.filter(
        owner=company, owner__role__user=request.user).distinct()

    data = {
        'company': settings.SITE.canonical_company,
        'jobs': jobs.filter(owner=company, owner__role__user=request.user),
        'active_products': products.filter(expiration_date__gte=date.today()),
        'expired_products': products.filter(expiration_date__lt=date.today()),
    }
    return render_to_response('postajob/purchasedproducts_overview.html',
                              data, RequestContext(request))


@user_is_allowed()
def purchasedjobs_overview(request, purchased_product, admin):
    """
    Normally we would need to filter by settings.SITE for objects in postajob
    but this is already done from a previous view.
    """
    product = PurchasedProduct.objects.prefetch_related(
        'purchasedjob_set').get(pk=purchased_product)

    if admin:
        company = product.product.owner
    else:
        company = product.owner

    if not request.user.can(company, 'read purchased job'):
        return MissingActivity()

    jobs = product.purchasedjob_set.all()
    data = {
        'company': company,
        'purchased_product': product,
        'active_jobs': jobs.filter(is_expired=False),
        'expired_jobs': jobs.filter(is_expired=True)
    }
    if admin:
        return render_to_response(
            'postajob/purchasedjobs_admin_overview.html',
            data, RequestContext(request))
    else:
        return render_to_response('postajob/purchasedjobs_overview.html',
                                  data, RequestContext(request))


@user_is_allowed()
def purchasedmicrosite_admin_overview(request):
    company = settings.SITE.canonical_company
    has_access = request.user.can(company, 'read product', 'read request',
                                  'read offline purchase',
                                  'read purchased product', 'read grouping',
                                  compare=at_least_one)
    if not has_access:
        return MissingActivity()

    sites = settings.SITE.postajob_site_list()
    products = Product.objects.filter_by_sites(sites)
    purchased = PurchasedProduct.objects.filter_by_sites(sites)
    groupings = ProductGrouping.objects.filter_by_sites(sites)
    offline_purchases = OfflinePurchase.objects.filter_by_sites(sites)
    requests = Request.objects.filter_by_sites(sites)

    data = {
        'products': products.filter(owner=company)[:3],
        'product_groupings': groupings.filter(owner=company)[:3],
        'purchased_products': purchased.filter(product__owner=company)[:3],
        'offline_purchases': offline_purchases.filter(owner=company)[:3],
        'requests': requests.filter(owner=company)[:3],
        'company': company
    }

    return render_to_response('postajob/admin_overview.html', data,
                              RequestContext(request))


@user_is_allowed()
@requires('read product')
def admin_products(request):
    company = get_company(request)
    if settings.SITE:
        sites = settings.SITE.postajob_site_list()
        products = Product.objects.filter_by_sites(sites)
    else:
        products = Product.objects.all()
    data = {
        'products': products.filter(owner=company),
        'company': company,
    }
    return render_to_response('postajob/products.html', data,
                              RequestContext(request))


@user_is_allowed()
@requires('read grouping')
def admin_groupings(request):
    company = get_company(request)
    if settings.SITE:
        sites = settings.SITE.postajob_site_list()
        grouping = ProductGrouping.objects.filter_by_sites(sites)
    else:
        grouping = ProductGrouping.objects.all()
    data = {
        'product_groupings': grouping.filter(owner=company),
        'company': company,
    }
    return render_to_response('postajob/productgrouping.html', data,
                              RequestContext(request))


@user_is_allowed()
@requires('read offline purchase')
def admin_offlinepurchase(request):
    company = get_company(request)
    sites = settings.SITE.postajob_site_list()
    purchases = OfflinePurchase.objects.filter_by_sites(sites)
    data = {
        'offline_purchases': purchases.filter(owner=company),
        'company': company,
    }
    return render_to_response('postajob/offlinepurchase.html', data,
                              RequestContext(request))


@user_is_allowed()
@requires("read request")
def admin_request(request):
    company = get_company(request)
    sites = settings.SITE.postajob_site_list()
    requests = Request.objects.filter_by_sites(sites)

    data = {
        'company': company,
        'pending_requests': requests.filter(owner=company, action_taken=False),
        'processed_requests': requests.filter(owner=company, action_taken=True)
    }

    return render_to_response('postajob/request.html', data,
                              RequestContext(request))


@user_is_allowed()
@requires('read purchased product')
def admin_purchasedproduct(request):
    company = get_company(request)
    sites = settings.SITE.postajob_site_list()
    purchases = PurchasedProduct.objects.filter_by_sites(sites).filter(
        product__owner=company)
    data = {
        'company': company,
        'active_products': purchases.filter(expiration_date__gte=date.today()),
        'expired_products': purchases.filter(expiration_date__lt=date.today()),
    }

    return render_to_response('postajob/purchasedproduct.html', data,
                              RequestContext(request))

def view_request(request, pk, model=None):
    template = 'postajob/request/{model}.html'
    company = get_company(request)
    model = model or Request

    request_kwargs = {
        'pk': pk,
        'owner': company
    }

    request_made = get_object_or_404(model, **request_kwargs)
    if model == Request:
        activity = "read request"
        request_object = request_made.request_object()
    else:
        activity = "read offline purchase"
        request_object = request_made

    content_type = ContentType.objects.get_for_model(type(request_object))

    data = {
        'company': company,
        'content_type': content_type,
        'object': request_object,
        'request_obj': request_made,
    }

    if not request.user.can(company, activity):
        return MissingActivity()

    return render_to_response(template.format(model=content_type.model),
                              data, RequestContext(request))


@user_is_allowed()
@requires("update request")
def process_admin_request(request, pk, approve=True,
                          block=False):
    """
    Marks a Request as action taken on it and sets the corresponding object's
    approval status. Assumes the object has an is_approved field.

    Adds the requesting user (if one exists) to the company's block list
    if the block parameter is True.

    """
    company = get_company(request)
    request_made = get_object_or_404(Request, pk=pk, owner=company)
    content_type = request_made.content_type
    request_object = request_made.request_object()

    if request_object and request_object.user_has_access(request.user):
        if block and request_object.created_by:
            # Block the user that initiated this request
            # and deny all of that user's outstanding requests
            profile, _ = CompanyProfile.objects.get_or_create(
                company=company)
            profile.blocked_users.add(request_object.created_by)

            # Since Requests and the objects associated with them are related
            # using a fake foreign key, we have to do multiple queries. We
            # could potentially get away with only the first two, but the last
            # one is included just to be safe.
            request_objects = content_type.model_class().objects.filter(
                created_by=request_object.created_by,
                owner=request_object.owner,
                is_approved=False)
            requests = Request.objects.filter(
                object_id__in=request_objects.values_list('pk', flat=True),
                action_taken=False).values_list('object_id', flat=True)
            request_objects = request_objects.filter(
                pk__in=requests)

            reason = request.REQUEST.get('block-reason', '')
            requests.update(action_taken=True, deny_reason=reason)
            request_objects.update(is_approved=False)
        else:
            request_object.is_approved = approve
            request_object.save()
            if not approve:
                request_made.deny_reason = request.REQUEST.get('deny-reason',
                                                               '')
            request_made.action_taken = True
            request_made.save()

    return redirect('request')


def product_listing(request):
    site = settings.SITE
    company = site.canonical_company

    # Get all site packages and products for a site.
    site_packages = site.sitepackage_set.all()
    products = Product.objects.filter(package__sitepackage__in=site_packages)

    # Group products by the site package they belong to.
    groupings = set()
    for product in products:
        profile = get_object_or_none(CompanyProfile, company=product.owner)
        if product.cost < 0.01 or (profile and profile.authorize_net_login and
                                   profile.authorize_net_transaction_key):
            groupings = groupings.union(
                set(product.productgrouping_set.filter(is_displayed=True,
                                                       products__isnull=False)))

    # Sort the grouped packages by the specified display order.
    groupings = sorted(groupings, key=lambda grouping: grouping.display_order)

    return render_to_response('postajob/package_list.html',
                              {'product_groupings': groupings,
                               'company': company},
                              RequestContext(request))


@user_is_allowed()
@requires('read grouping')
def order_postajob(request):
    """
    This view will always get two variables and always switches display_order.

    """
    models = {
        'groupings': ProductGrouping
    }

    company = get_company_or_404(request)
    obj_type = request.GET.get('obj_type')
    # Variables

    try:
        model = models[obj_type]
    except KeyError:
        raise Http404("postajob.views.order_postajob: object type "
                      "not supported")

    a = model.objects.get(pk=request.GET.get('a'))
    b = model.objects.get(pk=request.GET.get('b'))

    # Swap two variables
    a.display_order, b.display_order = b.display_order, a.display_order

    # Save Objects
    a.save()
    b.save()

    data = {
        'order': True,
        'product_groupings': ProductGrouping.objects.filter(owner=company),
    }

    # Render updated rows
    html = render_to_response('postajob/includes/productgroup_rows.html', data,
                              RequestContext(request))
    return html


@csrf_exempt
@user_is_allowed()
@requires('read invoice')
def resend_invoice(request, pk):
    company = get_company(request)

    product = PurchasedProduct.objects.get(pk=pk, product__owner=company)
    product.invoice.send_invoice_email(send_to_admins=False,
                                       other_recipients=[request.user.email])
    data = {'purchased_product': pk}
    redirect_url = reverse('admin_view_invoice', kwargs=data) + '?m=success'
    return HttpResponseRedirect(redirect_url)


class PostajobModelFormMixin(object):
    """
    A mixin for postajob models, since nearly all of them rely on
    owner for filtering by company.

    """
    model = None
    prevent_delete = False
    template_name = 'postajob/form.html'

    def get_queryset(self, request):
        kwargs = {'owner__in': request.user.roles.values('company')}
        self.queryset = self.model.objects.filter(**kwargs)
        return self.queryset

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        kwargs['company'] = get_company(self.request)
        kwargs['prevent_delete'] = self.prevent_delete

        return super(PostajobModelFormMixin, self).get_context_data(**kwargs)


class BaseJobFormView(PostajobModelFormMixin, RequestFormViewBase):
    """
    A mixin for job purchase formviews. JobFormView and PurchasedJobFormView
    share this exact functionality.
    """
    prevent_delete = True

    def delete(self, request):
        raise Http404("postajob.views.BaseJobFormView: delete not allowed")

    def get_context_data(self, **kwargs):
        context = super(BaseJobFormView, self).get_context_data(**kwargs)
        if context.get('item', None):
            formset_qs = JobLocation.objects.filter(jobs=context['item'])
        else:
            formset_qs = JobLocation.objects.none()
        if self.request.POST:
            delete = []
            for key in self.request.POST.keys():
                # JobLocationFormSet has a custom save that accepts the indices
                # of forms to be deleted; The following constructs that list.
                if key.endswith('DELETE') and '__prefix__' not in key:
                    location_num = int(key.split('-')[1])
                    delete.append(location_num)
            context['delete'] = delete
            context['formset'] = JobLocationFormSet(self.request.POST,
                                                    queryset=formset_qs)
        else:
            context['formset'] = JobLocationFormSet(queryset=formset_qs)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        joblocation_formset = context['formset']
        if form.is_valid():
            if joblocation_formset.is_valid():
                job = form.save()
                locations = joblocation_formset.save(delete=context['delete'])
                for location in locations:
                    location.jobs.add(job)
                job.save()
                return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))


class JobFormView(BaseJobFormView):
    form_class = JobForm
    model = Job
    display_name = 'Job'
    template_name = 'postajob/job_form.html'

    success_url = reverse_lazy('jobs_overview')
    add_name = 'job_add'
    update_name = 'job_update'
    delete_name = 'job_delete'

    @method_decorator(user_is_allowed())
    def dispatch(self, *args, **kwargs):
        """
        Decorators on this function will be run on every request that
        goes through this class.

        """
        return super(JobFormView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        company = get_company_or_404(self.request)
        if not can_modify(self.request.user, company, kwargs,
                          "update job", "create job"):
            return MissingActivity()

        return super(JobFormView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        company = get_company_or_404(self.request)
        if not can_modify(self.request.user, company, kwargs,
                          "update job", "create job"):
            return MissingActivity()

        return super(JobFormView, self).post(*args, **kwargs)

    def get_queryset(self, request):
        super(JobFormView, self).get_queryset(request)
        kwargs = {'purchasedjob__isnull': True}
        self.queryset = self.queryset.filter(**kwargs)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super(JobFormView, self).get_context_data(**kwargs)
        context['order_type'] = 'job'
        return context


class PurchasedJobFormView(BaseJobFormView):
    form_class = PurchasedJobForm
    model = PurchasedJob
    display_name = '{product} Job'

    success_url = reverse_lazy('purchasedproducts_overview')
    add_name = 'purchasedjob_add'
    update_name = 'purchasedjob_update'
    delete_name = 'purchasedjob_delete'
    template_name = 'postajob/job_form.html'

    purchase_field = 'purchased_product'
    purchase_model = PurchasedProduct

    def set_object(self, *args, **kwargs):
        if resolve(self.request.path).url_name == self.add_name:
            http404_view = "postajob.views.PurchasedJobFormView"
            if not self.product.can_post_more():
                # If more jobs can't be posted to the product, don't allow
                # the user to access the add view.
                raise Http404("{view}: all available jobs for this posting "
                              "have been used".format(view=http404_view))
            else:
                company = self.product.product.owner
                if company and hasattr(company, 'companyprofile'):
                    if self.request.user in company.companyprofile.blocked_users.all():
                        # If the current user has been blocked by the company
                        # that we are trying to post a job to, don't allow
                        # the user to access the add view.
                        raise Http404("{view}: user is blocked from posting "
                                      "to this company".format(
                                          view=http404_view))

        return super(PurchasedJobFormView, self).set_object(*args, **kwargs)

    @method_decorator(user_is_allowed())
    def dispatch(self, *args, **kwargs):
        """
        Determine and set which product is attempting to be purchased.

        """
        # The add url also has the pk for the product they're attempting
        # to purchase.
        if kwargs.get('product'):
            self.product = get_object_or_404(self.purchase_model,
                                             pk=kwargs.get('product'))
        else:
            obj = get_object_or_404(self.model, pk=kwargs.get('pk'))
            self.product = getattr(obj, self.purchase_field, None)

        # Set the display name based on the model
        self.display_name = self.display_name.format(product=self.product)

        return super(PurchasedJobFormView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        company = get_company_or_404(self.request)

        if not can_modify(self.request.user, company, kwargs,
                          "update purchased job", "create purchased job"):
            return MissingActivity()

        return super(PurchasedJobFormView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        company = get_company_or_404(self.request)

        if not can_modify(self.request.user, company, kwargs,
                          "update purchased job", "create purchased job"):
            return MissingActivity()

        return super(PurchasedJobFormView, self).post(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PurchasedJobFormView, self).get_form_kwargs()
        kwargs['product'] = self.product
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PurchasedJobFormView, self).get_context_data(**kwargs)
        context['order_type'] = 'purchasedjob'
        return context


class ProductFormView(PostajobModelFormMixin, RequestFormViewBase):
    form_class = ProductForm
    model = Product
    display_name = 'Product'
    prevent_delete = True

    success_url = reverse_lazy('product')
    add_name = 'product_add'
    update_name = 'product_update'

    def get(self, *args, **kwargs):
        company = get_company_or_404(self.request)
        if not can_modify(self.request.user, company, kwargs,
                          "update product", "create product"):
            return MissingActivity()

        return super(ProductFormView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        company = get_company_or_404(self.request)
        if not can_modify(self.request.user, company, kwargs,
                          "update product", "create product"):
            return MissingActivity()
        return super(ProductFormView, self).post(*args, **kwargs)

    @method_decorator(user_is_allowed())
    def dispatch(self, *args, **kwargs):
        """
        Decorators on this function will be run on every request that
        goes through this class.

        """
        return super(ProductFormView, self).dispatch(*args, **kwargs)


class ProductGroupingFormView(PostajobModelFormMixin, RequestFormViewBase):
    form_class = ProductGroupingForm
    model = ProductGrouping
    display_name = 'Product Grouping'

    success_url = reverse_lazy('productgrouping')
    add_name = 'productgrouping_add'
    update_name = 'productgrouping_update'
    delete_name = 'productgrouping_delete'

    def get(self, *args, **kwargs):
        company = get_company_or_404(self.request)
        if not can_modify(self.request.user, company, kwargs,
                          "update grouping", "create grouping"):
            return MissingActivity()
        return super(ProductGroupingFormView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        company = get_company_or_404(self.request)
        if not can_modify(self.request.user, company, kwargs,
                          "update grouping", "create grouping"):
            return MissingActivity()
        return super(ProductGroupingFormView, self).post(*args, **kwargs)

    def delete(self, request):
        company = get_company_or_404(self.request)
        if self.request.user.can(company, 'delete grouping'):
            return super(ProductGroupingFormView, self).delete(request)
        return MissingActivity()

    @method_decorator(user_is_allowed())
    def dispatch(self, *args, **kwargs):
        """
        Decorators on this function will be run on every request that
        goes through this class.

        """
        return super(ProductGroupingFormView, self).dispatch(*args, **kwargs)


class PurchasedProductFormView(PostajobModelFormMixin, RequestFormViewBase):
    form_class = PurchasedProductForm
    model = PurchasedProduct
    # The display name is determined by the product id and set in dispatch().
    display_name = '{product} - Billing Information'

    success_url = reverse_lazy('purchasedproducts_overview')
    add_name = 'purchasedproduct_add'
    update_name = 'purchasedproduct_update'
    delete_name = 'purchasedproduct_delete'

    purchase_field = 'product'
    purchase_model = Product

    @method_decorator(user_is_allowed())
    def dispatch(self, *args, **kwargs):
        """
        Determine and set which product is attempting to be purchased.

        """
        # The add url also has the pk for the product they're attempting
        # to purchase.

        self.product = get_object_or_404(self.purchase_model,
                                         pk=kwargs.get('product'))

        # Set the display name based on the model
        self.display_name = self.display_name.format(product=self.product)

        # If the product is free but the current user has no companies or an
        # un-filled-out profile, use the product form that only gets company
        # information.
        if self.product.cost < 0.01:
            company = get_company(self.request)
            profile = get_object_or_none(CompanyProfile, company=company)

            if company and profile and profile.address_line_one:
                invoice = Invoice.objects.create(
                    transaction_type=Invoice.FREE,
                    first_name=self.request.user.first_name,
                    last_name=self.request.user.last_name,
                    address_line_one=profile.address_line_one,
                    address_line_two=profile.address_line_two,
                    city=profile.city,
                    state=profile.state,
                    country=profile.country,
                    zipcode=profile.zipcode,
                    owner=self.product.owner,
                )
                purchase_kwargs = {
                    'product': self.product,
                    'invoice': invoice,
                    'owner': company,
                    'paid': True,
                }
                PurchasedProduct.objects.create(**purchase_kwargs)
                return redirect(self.success_url)
            else:
                self.display_name = self.product
                self.form_class = PurchasedProductNoPurchaseForm
        return super(PurchasedProductFormView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PurchasedProductFormView, self).get_form_kwargs()
        kwargs['product'] = self.product
        return kwargs

    def set_object(self, request):
        """
        Purchased products can't be edited or deleted, so prevent anyone
        getting an actual object to edit/delete.

        """
        self.object = None
        if not resolve(request.path).url_name.endswith('_add'):
            raise Http404("postajob.views.PurchasedProductFormView: "
                          "PurchasedProducts can't be edited or deleted")

    def get_context_data(self, **kwargs):
        context = super(PurchasedProductFormView, self).get_context_data(**kwargs)
        context['submit_btn_name'] = 'Buy'
        context['submit_text'] = 'Your card will be charged when you click \"Buy\"'
        context['sidebar'] = True
        context['product'] = self.product
        return context


class OfflinePurchaseFormView(PostajobModelFormMixin, RequestFormViewBase):
    form_class = OfflinePurchaseForm
    model = OfflinePurchase
    display_name = 'Offline Purchase'

    success_url = reverse_lazy('offlinepurchase')
    add_name = 'offlinepurchase_add'
    update_name = 'offlinepurchase_update'
    delete_name = 'offlinepurchase_delete'

    @method_decorator(requires("delete offline purchase"))
    def delete(self, request):
        if self.object.redeemed_on:
            raise Http404("postajob.views.OfflinePurchaseFormView: "
                          "can't delete redeemed OfflinePurchases")
        return super(OfflinePurchaseFormView, self).delete(request)

    @method_decorator(user_is_allowed())
    def dispatch(self, *args, **kwargs):
        """
        Decorators on this function will be run on every request that
        goes through this class.

        """
        return super(OfflinePurchaseFormView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        if resolve(self.request.path).url_name == self.add_name:
            kwargs = {
                'pk': self.object.pk,
            }
            return reverse('offline_purchase_success', kwargs=kwargs)
        return self.success_url

    def set_object(self, request):
        """
        Attempting to determine what happens to Products in an already-redeemed
        OfflinePurchase is nearly impossible, so OfflinePurchases can
        only be added or deleted.

        """
        acceptable_names = [self.add_name, self.delete_name]
        if resolve(request.path).url_name not in acceptable_names:
            raise Http404("postajob.views.OfflinePurchaseFormView: "
                          "OfflinePurchases can only be added or deleted")
        return super(OfflinePurchaseFormView, self).set_object(request)

    def get(self, *args, **kwargs):
        company = get_company_or_404(self.request)
        if not can_modify(self.request.user, company, kwargs,
                          "update offline purchase",
                          "create offline purchase"):
            return MissingActivity()

        return super(OfflinePurchaseFormView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        company = get_company_or_404(self.request)
        if not can_modify(self.request.user, company, kwargs,
                          "update offline purchase",
                          "create offline purchase"):
            return MissingActivity()

        return super(OfflinePurchaseFormView, self).post(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OfflinePurchaseFormView, self).get_context_data(**kwargs)
        context['show_product_labels'] = True

        return context


class OfflinePurchaseRedemptionFormView(PostajobModelFormMixin,
                                        RequestFormViewBase):
    form_class = OfflinePurchaseRedemptionForm
    model = OfflinePurchase
    display_name = 'Offline Purchase'

    success_url = reverse_lazy('purchasedproducts_overview')
    add_name = 'offlinepurchase_redeem'
    update_name = None
    delete_name = None

    @method_decorator(user_is_allowed())
    def dispatch(self, *args, **kwargs):
        """
        Decorators on this function will be run on every request that
        goes through this class.

        """
        return super(OfflinePurchaseRedemptionFormView, self).dispatch(
            *args, **kwargs)

    def set_object(self, request):
        """
        OfflinePurchases can only be redeemed (added) by generic users.

        """
        self.object = None
        if not resolve(request.path).url_name == self.add_name:
            raise Http404("postajob.views.OfflinePurchaseRedemptionFormView: "
                          "OfflinePurchases can only be redeemed, not edited "
                          "or deleted, by third-party users")


class CompanyProfileFormView(PostajobModelFormMixin, RequestFormViewBase):
    form_class = CompanyProfileForm
    model = CompanyProfile
    prevent_delete = True
    display_name = 'Company Profile'

    success_url = reverse_lazy('purchasedmicrosite_admin_overview')
    add_name = 'companyprofile_add'
    update_name = 'companyprofile_edit'
    delete_name = 'companyprofile_delete'

    @method_decorator(user_is_allowed())
    def dispatch(self, *args, **kwargs):
        """
        Decorators on this function will be run on every request that
        goes through this class.

        """
        return super(CompanyProfileFormView, self).dispatch(*args, **kwargs)

    def set_object(self, *args, **kwargs):
        """
        Every add is actually an edit.

        """
        company = get_company_or_404(self.request)
        kwargs = {'company': company}
        self.object, _ = self.model.objects.get_or_create(**kwargs)
        return self.object

    def delete(self, request):
        raise Http404("postajob.views.CompanyProfileFormView: "
                      "delete not allowed")

    def get_context_data(self, **kwargs):
        context = super(CompanyProfileFormView, self).get_context_data(
            **kwargs)
        company = get_company(self.request)
        context.setdefault('company', company)

        return context


class SitePackageFilter(FSMView):
    model = SeoSite
    fields = ('domain__icontains', )

    def get(self, request):
        self.request = request
        return super(SitePackageFilter, self).get(request)

    def get_queryset(self):
        company = get_company_or_404(self.request)
        sites = company.get_seo_sites()
        return sites


@user_is_allowed()
@requires("update request")
def blocked_user_management(request):
    """
    Displays blocked users (if any) for the current company as well as
    an unblock link.
    """
    company = get_company_or_404(request)
    profile = CompanyProfile.objects.get_or_create(company=company)[0]
    blocked_users = profile.blocked_users.all()
    data = {
        'company': company,
        'blocked_users': blocked_users
    }
    return render_to_response('postajob/blocked_user_management.html', data,
                              RequestContext(request))


@user_is_allowed()
@requires("update request")
def unblock_user(request, pk):
    """
    Unblocks a given user that has previously been blocked from posting jobs.

    Inputs:
    :pk: ID of user that has been blocked
    """
    company = get_company_or_404(request)
    profile = company.companyprofile
    if profile:
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            pass
        else:
            profile.blocked_users.remove(user)
    return redirect(reverse('blocked_user_management'))


def ajax_regions(request):
    if request.is_ajax() and 'country' in request.GET:
        country = request.GET.get('country')
        states = state_list(country)
        return HttpResponse(json.dumps(states))
