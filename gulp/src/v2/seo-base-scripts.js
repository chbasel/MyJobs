/* global $ */
/* eslint-disable */
/**
 * Legacy es5.1 functions used in seo_base_v2.html template,
 * relocated to the gulp directory to utilize es6, webpack, et al, during Sprint 24-2016.
 * ESLint stills complains about coding styles, however, for certain
 * variable/property names, we still need the underscore casing to work with python codes.
 * TODO: Refactor 'pager' codes to be less verbose.
 * TODO: Convert function expressions to arrow functions where appropriate.
 **/

$(document).ready(function() {
  // needed to render 'topbar'
  if (typeof site_name !== 'undefined' && !$('*[data-widget_type=tools]').length) {
    getToolbar(site_name);
  }
  // Autocomplete functionality for the job,title,keyword input box.
  $('.micrositeTitleField').autocomplete({
    source: function (request, response) {
      $.ajax({
        url: '/ajax/ac/?lookup=title&term=' + request.term,
        dataType: 'jsonp',
        success: function (data) {
          response($.map(data, function(item) {
            return {
              label: item.title,
              value: item.title,
            };
          }));
        },
      });
    },
    open: function() {
      $('.ui-autocomplete li.ui-menu-item:odd').addClass('ui-menu-item-alternate');
      $('.ui-autocomplete li.ui-menu-item a').removeClass('ui-corner-all');
    },
    select: function (event, ui) {
      $('.micrositeTitleField').val('"' + ui.item.value + '"');
      return false;
    },
    minLength: 2,
  });
  // Autocomplete functionality for the city,state,country input box.
  $('.micrositeLocationField').autocomplete({
    source: function(request, response) {
      $.ajax({
        url: '/ajax/ac/?lookup=location&term=' + request.term,
        dataType: 'jsonp',
        success: function (data) {
          response($.map(data, function(item) {
            return {
              label: item.location + ' - (' + item.jobcount + ')',
              value: item.location,
            };
          }));
        },
      });
    },
    open: function() {
      $('.ui-autocomplete li.ui-menu-item:odd').addClass('ui-menu-item-alternate');
    },
    minLength: 2,
  });
  // Add syntax highlighting to autocomplete results.
  $.ui.autocomplete.prototype._renderItem = function(ul, item) {
    /**
     Inputs:
     :ul:    the autocomplete object to modify
     :item:  the individual item to modify
     Returns:
     Modified item
     **/
    let term = this.term;
    if ((term.charAt(0) === '"' && term.charAt(term.length - 1) === '"')) {
      term = this.term.substr(1, term.length - 2);
    } else {
      term = this.term.split(' ').join('|');
    }
    const re = new RegExp('(' + term + ')', 'gi');
    const t = item.label.replace(re, '<strong class="ac-highlight">$1</strong>');
    return $('<li></li>')
      .data('item.autocomplete', item)
      .append('<a>' + t + '</a>')
      .appendTo(ul);
  };
  // Size the width of the drop down list to match width of input, always, in any size, without CSS
  $.ui.autocomplete.prototype._resizeMenu = function() {
    const ul = this.menu.element;
    ul.outerWidth(this.element.outerWidth());
  };
  // Submit the search form if location AND title fields have a value in them (and MOC if applicable).
  $('#standardSearch input[type=text]').bind('autocompleteselect', function(event, ul) {
    /**
     Inputs:
     :event: The autocompleteselect event
     :ul: The autocomplete object (an unordered list)
     **/
    $(this).val(ul.item.value);
    if ($('#moc').length > 0) {
      if ($('#location').val() !== '' && $('#q').val() !== '' && $('#moc').val() !== '') {
        $('#standardSearch').submit();
      }
    } else {
      if ($('#location').val() !== '' && $('#q').val() !== '') {
        $('#standardSearch').submit();
      }
    }
  });
  // Add autocomplete functionality to the MOC/MOS search field.
  $('.micrositeMOCField').autocomplete({
    source: function (request, response) {
      $.ajax({
        url: '/ajax/mac/?lookup=moc&term=' + request.term,
        dataType: 'jsonp',
        success: function (data) {
          response($.map(data, function (item) {
            return {
              label: item.label,
              value: item.value,
              moc_id: item.moc_id,
            };
          }));
        },
      });
    },
    select: function(event, ui) {
      $('#moc_id').val(ui.item.moc_id);
    },
    open: function() {
      $('.ui-autocomplete li.ui-menu-item:odd').addClass('ui-menu-item-alternate');
    },
    minLength: 2,
  });
  // Clear moc_id value if moc is changed
  $('#moc').change(function() {
    $('#moc_id').val('');
  });
  // Save Search Functionality
  get_default_widget_html(false);
  // 'Pager' logic for the 'Show More' && 'Show Less' logic begins here
  const pager = new Pager();
  const total_clicks = parseInt(window.location.hash.slice(1, 10));
  if (!isNaN(total_clicks)) {
    // Only set hash if one already existed.
    window.location.hash = '';
  }
  $(document).on('click', 'a.direct_optionsMore', function(e) {
    const parent = $(this).parent();
    const num_items = parent.attr('data-num-items');
    return pager.showMoreHandler(e, num_items, parent);
  });
  $('#button_moreJobs').click(function(e) {
    e.preventDefault();
    const parent = $(this).parent();
    const num_items = parseInt(parent.attr('data-num-items'));
    const offset = parseInt(parent.attr('offset'));
    const path = window.location.pathname;
    const query = window.location.search;
    const ajax_url = path + 'ajax/joblisting/' + query;
    const hiddenFeaturedList = $('#direct_listingDiv .featured_jobListing.direct_hiddenOption .direct_joblisting');
    const hiddenDefaultList = $('#direct_listingDiv .default_jobListing.direct_hiddenOption .direct_joblisting');
    let focus_item;
    let firstItem;
    if (hiddenFeaturedList.length > 0) {
      firstItem = $(hiddenFeaturedList)[0];
    } else {
      firstItem = $(hiddenDefaultList)[0];
    }
    focus_item = $(firstItem).find('a');
    focus_item.focus();
    $('#direct_listingDiv .direct_hiddenOption').removeClass('direct_hiddenOption');
    $.ajax({
      url: ajax_url,
      data: {'num_items': num_items, 'offset': offset},
      success: function(data) {
        $('#direct_listingDiv ul:last').after(data);
        parent.attr('offset', (offset + num_items).toString());
        let num_clicks = parseInt(window.location.hash.slice(1, 10));
        if (isNaN(num_clicks) && isNaN(total_clicks)) {
          window.location.hash = '1';
        } else {
          if (isNaN(num_clicks)) {
            num_clicks = 0;
          }
          window.location.hash = (++num_clicks).toString();
          if (!isNaN(total_clicks) && num_clicks < total_clicks) {
            $('#button_moreJobs').click();
          }
        }
      },
    });
  });
  if (!isNaN(total_clicks)) {
    $('#button_moreJobs').trigger('click');
  }
  $('a.direct_optionsLess').click(function(e) {
    const parent = $(this).parent();
    const num_items = parent.attr('data-num-items');
    return pager.showLessHandler(e, num_items, parent);
  });
  $('.direct_offsiteContainer').hover(function() {
    $(this).children('.direct_offsiteHoverDiv').show();
  }, function() {
    $(this).children('.direct_offsiteHoverDiv').hide();
  });
  $('div.direct_offsiteHoverDiv').each(function() {
    $(this).attr('style', 'margin-top: -' + ($(this).height() + 2) + 'px;');
  });
  $('.direct_deBadgeLink').click(function() {
    goalClick('/G/de-click', this.href);
    return false;
  });
  $('.direct_companyLink').click(function() {
    goalClick('/G/career-site-click', this.href);
    return false;
  });
  $('.direct_socialLink').click(function() {
    goalClick('/G/social-media-click', this.href);
    return false;
  });
});

function getToolbar(site_name) {
  const site = encodeURIComponent(window.location.protocol + '//' + window.location.hostname);
  const url = ABSOLUTE_URL + 'topbar/?v2=1&site_name=' + site_name + '&site=' + site + '&impersonating=' + impersonating;
  $.ajax({
    url: url,
    dataType: 'jsonp',
    type: 'GET',
    jsonpCallback: 'populate_toolbar',
    crossDomain: true,
    processData: false,
    headers: {'Content-Type': 'application/json', Accept: 'text/javascript'},
  });
}

function populate_toolbar(data) {
  $('.direct_dotjobsWideHeader').prepend(data);
}

if (window) {
  window.populate_toolbar = populate_toolbar;
}

const SS_USERNAME = 'directseo@directemployersfoundation.org';
const SS_API_KEY = '6fcd589a4efa72de876edfff7ebf508bedd0ba3e';
const SS_API_STR = '&username=' + SS_USERNAME + '&api_key=' + SS_API_KEY;
const BASE_URL = 'https://secure.my.jobs';
const SS_URL = encodeURIComponent(window.location.href);

let most_recent_html = '';

function handle_error() {
  // Fills with the most recent text and then overwrites applicable parts
  // with the error message. Uses the most recent text to ensure formatting
  // and variables supplied by myjobs are persistent, so the experience
  // for logged in users continues to be the same.
  fill(most_recent_html);
  $('.saved-search-form').prepend('<em class="warning">Something went wrong!</em>');
  $('.saved-search-form > form > b').html('<p>Your search could not successfully be created.</p>');
  $('label[for="saved-search-email"]').html('<p>Your search could not successfully be created.</p>');
  $('.saved-search-button').html('Try saving this search again');
}

function fill(html) {
  $('#de-myjobs-widget').html(html);
  $('#mobile-de-myjobs-widget').html(html);
  most_recent_html = html;
}

if (window) {
  window.fill = fill;
}

function reload_default_widget(data) {
  if (data.error) {
    handle_error();
  } else {
    get_default_widget_html(true);
  }
}

function get_default_widget_html(success) {
  let ajax_url;
  if (success) {
    ajax_url = BASE_URL + '/saved-search/widget/?v2=1&callback=fill&success=' + user_email + '&url=' + SS_URL;
  } else {
    ajax_url = BASE_URL + '/saved-search/widget/?v2=1&callback=fill&url=' + SS_URL;
  }
  jsonp_ajax_call(ajax_url);
}

function create_saved_search() {
  jsonp_ajax_call(BASE_URL + '/api/v1/savedsearch/?callback=reload_default_widget&email=' + user_email + SS_API_STR + '&url=' + SS_URL);
}

if (window) {
  window.create_saved_search = create_saved_search;
}

function create_user() {
  jsonp_ajax_call(BASE_URL + '/api/v1/user/?callback=create_saved_search&email=' + user_email + SS_API_STR + '&source=' + window.location.hostname);
}

function save_search() {
  // If there is any hint that there isn't a well-defined user email
  // provided, attempts to get a user from the input and create a new user.
  // Otherwise, uses the currently provided user to create a saved search.
  if (user_email !== 'None' && user_email !== 'undefined' && user_email) {
    $('.saved-search-form').html('<em class="saved-search-widget-loading">Saving this search</em>');
    create_saved_search();
  } else {
    try {
      user_email = $('#saved-search-email').val();
      $('.saved-search-form').html('<em class="saved-search-widget-loading">Saving this search</em>');
      create_user();
    } catch (err) {
      handle_error();
    }
  }
}

if (window) {
  window.save_search = save_search;
}

function jsonp_ajax_call(ajax_url) {
  $.ajax({
    url: ajax_url,
    dataType: 'jsonp',
    type: 'GET',
    crossDomain: true,
    jsonp: false,
    processData: false,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/javascript',
    },
    complete: function() {
      $('#saved-search-email').keyup(function(event) {
        const ENTER = 13; // The keycode of the enter button
        if (event.which === ENTER) {
          save_search();
        }
      });
    },
  });
}

/*
 JAVASCRIPT FOR THE NEW REBRANDING HOMEPAGE FUNCTIONALITY
 */
// Javascript to show search criteria in mobile view
$('.mobile-search-btn').on('click', function() {
  $('.search-criteria-box').toggleClass('show-search-criteria');
});

// Javascript for showing the search facets in mobile view on click
$('#mobile_search').on('click', function() {
  const mobileSearchFacets = $('.mobile-search-facets');
  mobileSearchFacets.toggleClass('show-mobile-search-facets');
});

// Function for initializing the accordion of the search criteria
function filterAccordion() {
  const accordion = $('.filter-accordion');
  $.each(accordion, function() {
    const that = $(this);
    const panel = that.next('.filter-panel');
    const filterCaret = that.children('.drop-caret');
    that.on('click', function() {
      panel.toggleClass('filter-panel-deactive');
      filterCaret.toggleClass('caret-rotate');
    });
  });
}
filterAccordion();

// Javascript to cut the count off of the facets and place it separately into a span that floats to the right
// Might need to configure and change settings later to get rid of this function
$.each($('#direct_disambiguationDiv li a'), function() {
  const self = $(this);
  const text = self.text().split('(')[0];
  const count = self.text().split('(').pop();
  self.html(text);
  self.append('<span class="count"></span>');
  self.children('span').html('(' + count);
});

// Javascript to cut the count off the hidden facets and place it separately inside of a span that floats. The code
// above is duplicated but wouldn't work for the hidden LI that were created on the fly so I am dynamically doing it
// when there is a click event on the option to show more of the filters
$('.direct_optionsMore').on('click', function() {
  $.each($('#direct_disambiguationDiv li a'), function() {
    const self = $(this);
    const text = self.text().split('(')[0];
    const count = self.text().split('(').pop();
    self.html(text);
    self.append('<span class="count"></span>');
    self.children('span').html('(' + count);
  });
});

// Function for showing and hiding the header when scrolling in mobile view
function showHideHeaderScroll() {
  // Hide Header on on scroll down
  let didScroll;
  let lastScrollTop = 0;
  const delta = 5;
  const navbarHeight = $('nav.main-nav-topbar').outerHeight();
  const viewPort = $(window).width();
  // Checking to make sure a scroll has occured
  function hasScrolled() {
    const scrollTop = $(window).scrollTop();
    // Make sure they scroll more than delta
    if (Math.abs(lastScrollTop - scrollTop) <= delta) {
      return;
    }
    // If they scrolled down and are past the navbar, add class .nav-up.
    if (scrollTop > lastScrollTop && scrollTop > navbarHeight) {
      // Scroll Down
      $('nav.main-nav-topbar').removeClass('nav-down').addClass('nav-up');
    } else {
      // Scroll Up
      if (scrollTop + $(window).height() < $(document).height()) {
        $('nav.main-nav-topbar').removeClass('nav-up').addClass('nav-down');
      }
    }
    lastScrollTop = scrollTop;
  }
  // Checking to see if it's a mobile device or if the screensize is in mobile view
  if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || viewPort < 992) {
    $(window).scroll(() => {
      didScroll = true;
    });
    setInterval(() => {
      if (didScroll) {
        hasScrolled();
        didScroll = false;
      }
    }, 250);
  }
}

showHideHeaderScroll();

// Secure Block Begins.  Secure Block is on hold when this comment was written,
let saved_dashboard_url = '';

function secure_block(secure_block_url, request) {
  // need to explicitly marshal the result data into this deferred
  // because we are on old jQuery.
  const result = $.Deferred();
  $.ajax({
    type: 'OPTIONS',
    crossDomain: true,
  }).done(function(data, textStatus, xhr) {
    xhr_secure_block(secure_block_url, request).done(result.resolve).fail(result.reject);
  }).fail(function(xhr, textStatus, error) {
    jsonp_secure_block(secure_block_url, request).done(result.resolve).fail(result.reject);
  });
  return result.promise();
}

function xhr_secure_block(secure_block_url, data) {
  return $.ajax({
    url: secure_block_url,
    type: 'POST',
    headers: {'X-Requested-With': 'XMLHttpRequest'},
    data: JSON.stringify({'blocks': data}),
    contentType: 'application/json',
    xhrFields: {
      withCredentials: true,
    },
  });
}

if (window) {
  window.xhr_secure_block = xhr_secure_block;
}

function jsonp_secure_block(secure_block_url, data) {
  const json = JSON.stringify(data);
  return $.ajax({
    url: secure_block_url,
    type: 'GET',
    dataType: 'jsonp',
    data: {'blocks': json},
  });
}

if (window) {
  window.jsonp_secure_block = jsonp_secure_block;
}

function populate_secure_blocks(request, callback) {
  if (!$.isEmptyObject(request)) {
    secure_block(saved_dashboard_url, request).fail(function(xhr, text, error) {
      console.error('dashboard fail: ', xhr, text, error);
    }).done(function (data, text, xhr) {
      $.each(data, function (key, value) {
        $('[data-secure_block_id=' + key + ']').html(value);
      });
      if (typeof callback === 'function') {
        callback();
      }
    });
  }
}

function load_secure_blocks(dashboard_url) {
  // load secure blocks for all divs containing the proper data tag
  saved_dashboard_url = dashboard_url;
  const request = {};
  $('*[data-secure_block_id]').each(function(i, block) {
    const element_id = $(block).data('secure_block_id');
    request[element_id] = $(block).data();
  });
  populate_secure_blocks(request);
}

if (window) {
  window.load_secure_blocks = load_secure_blocks;
}

function reload_secure_block(block_id, callback) {
  // reload an individual secure block that may have changed state
  // callback is an optional argument of a function that should be called
  // upon completion of the reload
  const request = {};
  const block = $('[data-secure_block_id=' + block_id + ']');
  if (block) {
    request[block_id] = block.data();
    populate_secure_blocks(request, callback);
  }
}

// Show More && Show Less logic inside of the facets
function Pager() {
  this._PAGE_SIZE = 20;
  this._HIDDEN_CLASS_NAME = 'direct_hiddenOption';
}

Pager.prototype = {
  showLessHandler: function(e, num_items, parent) {
    // hide the items
    this._showLessItems(parent, num_items, num_items);
    // toggle more/less link, if needed
    this._toggleLessLink(parent, num_items);
    this._toggleMoreLink(parent);
    // stop default behavior of the link, since we're
    // not really using it as a link.  yeah, its not ideal.
    return false;
  },
  showMoreHandler: function(e, num_items, parent) {
    const type = parent.attr('data-type');
    this._showMoreItems(num_items, type, parent);
    // toggle more/less links, if needed
    this._toggleLessLink(parent, num_items);
    // stop default behavior of the link, since we're
    // not really using it as a link.  yeah, its not ideal.
    return false;
  },
  _toggleLessLink: function(moreLessSpan, minVisible) {
    /* Turn the 'Less' link off when we're at the minVisible limit. */
    const relatedList = this._getListFromMoreLessLinksSpan(moreLessSpan);
    const lessLink = moreLessSpan.children('.direct_optionsLess')[0];
    const moreLink = moreLessSpan.children('.direct_optionsMore')[0];
    const currNumVisible = relatedList.children(':visible').length;
    if (currNumVisible > minVisible) {
      $(lessLink).show();
    } else {
      $(lessLink).hide();
      $(moreLink).focus();
    }
  },
  _toggleMoreLink: function(moreLessSpan) {
    const relatedList = this._getListFromMoreLessLinksSpan(moreLessSpan);
    const numHiddenItems = relatedList.children('.' + this._HIDDEN_CLASS_NAME).length;
    const moreLink = moreLessSpan.children('.direct_optionsMore')[0];
    (numHiddenItems > 0) ? $(moreLink).show() : $(moreLink).hide();
  },
  _getListFromMoreLessLinksSpan: function(moreLessSpan) {
    // The container for all the facet blocks.
    const parentDiv = $(moreLessSpan).parent();
    // From the container for all the facet blocks we can get the
    // exact list we want to work with.
    const itemListId = this._getListElementFromContainerId(moreLessSpan.attr('id'));
    return $(parentDiv).children('#' + itemListId);
  },
  _getListElementFromContainerId: function(linkContainerId) {
    // Current List IDs that we'll be looking for:
    // - direct_titleDisambig
    // - direct_countryDisambig
    // - direct_stateDisambig
    // - direct_cityDisambig
    // - direct_jobListing
    // - direct_facetDisambig
    // - direct_mocDisambig
    // We've attached the second part onto the ID of
    // the <span> tag that wraps the more/less links,
    // so we can pull it off of there to know which
    // list we should take action on.
    // i.e. <span id="direct_moreLessLinks_countryDisambig">
    const baseElementId = 'direct_%s';
    const idPieces = linkContainerId.split('_');
    const listId = idPieces[2];
    return baseElementId.replace('%s', listId);
  },
  _showMoreItems: function(numToShow, type, parent) {
    const relatedList = this._getListFromMoreLessLinksSpan(parent);
    const hiddenItems = relatedList.children('.' + this._HIDDEN_CLASS_NAME);
    let currNumHidden = hiddenItems.length;
    const focus_item = relatedList.children(this._HIDDEN_CLASS_NAME + ':first li');
    // if we have current hidden ones, lets show those
    if (currNumHidden > 0) {
      // if there's less hidden items than what we want to show
      // then we'll only show those and if there's zero hidden,
      // then we'll go get some more and still show the number
      // we want to
      numToShow = (numToShow > currNumHidden) ? currNumHidden : numToShow;
      hiddenItems.slice(0, numToShow).removeClass(this._HIDDEN_CLASS_NAME);
      currNumHidden -= numToShow;
    }
    if (currNumHidden === 0) {
      // lets see if we have any to get from the server
      const data = {
        'offset': parent.attr('data-offset'),
        'num_items': this._PAGE_SIZE,
      };
      const qsParams = this._getQueryParams();
      data.q = qsParams.q;
      data.location = qsParams.location;
      data.moc = qsParams.moc;
      data.company = qsParams.company;
      data.filter_path = window.location.pathname;
      this._ajax_getItems(type, data, parent);
    }
    focus_item.focus();
  },
  _showLessItems: function(parent, numToHide, minVisible) {
    const relatedList = this._getListFromMoreLessLinksSpan(parent);
    const visibleItems = relatedList.children(':visible');
    const numVisible = visibleItems.length;
    const numAvailableToHide = numVisible - minVisible;
    if (numAvailableToHide < numToHide) {
      numToHide = numAvailableToHide;
    }
    if (numToHide > 0) {
      visibleItems.slice(-numToHide).addClass(this._HIDDEN_CLASS_NAME);
    }
  },
  _ajax_getItems: function(type, data, parent) {
    // Preserve the reference to "this" so it can be used inside the
    // ajax call.
    const alsoThis = this;
    const url = this._build_url(type);
    if (url) {
      $.get(
        url,
        data,
        function(html) {
          alsoThis._getItemsSuccessHandler(html, parent);
        }
      );
    } else {
      alsoThis._getItemsSuccessHandler('', parent);
    }
  },
  _build_url: function(type) {
    // Build the URL with the current path as our
    // 'filter' that is sent into to filter objects
    const urls = {
      'title': '/ajax/titles/',
      'city': '/ajax/cities/',
      'state': '/ajax/states/',
      'country': '/ajax/countries/',
      'facet': '/ajax/facets/',
      'facet-2': '/ajax/facets/',
      'facet-3': '/ajax/facets/',
      'moc': '/ajax/mocs/',
      'mappedmoc': '/ajax/mapped/',
      'company': '/ajax/company-ajax/',
      'listing': '/ajax/joblisting/',
      'search': '/ajax/joblisting/',
    };
    return urls[type];
  },
  _getItemsSuccessHandler: function(html, parent) {
    // Since the update was successful, the offset can be updated to
    // reflect the requested amount.
    parent.attr('data-offset', parseInt(parent.attr('data-offset')) + this._PAGE_SIZE);
    // From the Django templates we get a lot of line breaks,
    // so we'll remove them right here, just to be safe.
    html = html.replace(/\n/g, '');
    const parentDiv = $(parent).parent();
    const itemListId = this._getListElementFromContainerId(parent.attr('id'));
    const relatedList = $(parentDiv).children('#' + itemListId);
    $(relatedList).children(':last').after(html);
    this._toggleMoreLink(parent);
  },
  _getQueryParams: function() {
    const result = {};
    const queryString = location.search.substring(1);
    const re = /([^&=]+)=([^&+]*)/g;
    let m;
    while (m = re.exec(queryString)) {
      result[decodeURIComponent(m[1])] = decodeURIComponent(m[2]);
    }
    return result;
  },
};
