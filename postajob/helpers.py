from myjobs.models import AppAccess
from postajob.models import SitePackage
from myblocks.models import Page, Row, RowOrder, LoginBlock, BlockOrder

def can_modify(user, company, kwargs, update_activity, create_activity):
    """
    Checks if user has update permission when a pk is available, otherwise
    checks for create permission.

    Inputs:
        :user: User to check activities against
        :company: The company being accessed.
        :kwargs: The keyword arguments passed to the view using this helper.
        :update_activity: The activity to check when the user wants to perform
                          an update action.
        :create_activity: The activity to check when the user wants to perform
                          a create action.

    Output:
        A boolean representing whether or not they had permission to perform
        the particular set of actions.

    Example::

        if not can_modify(user, company, kwargs, "update job", "create job"):
            return MissingActivity()

        retunr HttpResponse("Success")

    """
    if 'pk' in kwargs:
        return user.can(company, update_activity)
    else:
        return user.can(company, create_activity)

def enable_posting(company, site):
    """
    Convenience function which enables posting for a company by:
        - setting the site's canonical_company to company
        - enabling "Posting" access for the company
        - creating a site package with site in it, owned by company

    Inputs:
    :company: The ``Company`` to add posting access for
    :site: The ``SeoSite`` where jobs will be posted

    Output:
    A reference to the created SitePackage

    """
    # tie the company to the site
    site.canonical_company = company
    site.save()

    # enable posting access for the company
    company.app_access.add(AppAccess.objects.get(name='Posting'))

    # create a login block so that users can log in
    page = Page.objects.create(
        name="%s Login Page" % company.name, page_type=Page.LOGIN)
    page.sites.add(site)
    row = Row.objects.create()
    row_order = RowOrder.objects.create(row=row, page=page, order=0)
    login_block = LoginBlock.objects.create(
        name="%s Login Block" % company.name, offset=0, span=12)
    BlockOrder.objects.create(block=login_block, row=row, order=0)

    # create a site package for the posted jobs to live on
    package, _ = SitePackage.objects.get_or_create(
        owner=company, name="%s Sites" % company.name)
    package.sites.add(site)

    return package


def enable_marketplace(company, site):
    """
    Convenience function which enables marketplace for a company by:
        - setting the site's canonical_company to company
        - enabling "Marketplace" access for the company
        - creating a site package with site in it, owned by company
        - creating a login page to be used for admin

    Inputs:
    :company: The ``Company`` to add posting access for
    :site: The ``SeoSite`` where jobs will be posted

    Output:
    A reference to the created SitePackage

    """
    # tie the company to the site
    site.canonical_company = company
    site.save()

    # enable posting access for the company
    company.app_access.add(AppAccess.objects.get(name='MarketPlace'))

    # create a login block so that users can log in
    page = Page.objects.create(
        name="%s Login Page" % company.name, page_type=Page.LOGIN)
    page.sites.add(site)
    row = Row.objects.create()
    row_order = RowOrder.objects.create(row=row, page=page, order=0)
    login_block = LoginBlock.objects.create(
        name="%s Login Block" % company.name, offset=0, span=12)
    BlockOrder.objects.create(block=login_block, row=row, order=0)

    # create a site package for the posted jobs to live on
    package, _ = SitePackage.objects.get_or_create(
        owner=company, name="%s Sites" % company.name)
    package.sites.add(site)

    return package
