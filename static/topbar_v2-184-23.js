var utils = {};
var timer;

/**
 * Returns the value of the cookie. Returns null if that cookie is not found.
 * cookie: The name of the cookie to retrieve.
 **/
utils.readCookie = function readCookie(cookie) {
  var nameEQ = cookie + '=';
  var ca = document.cookie.split(';');
  var i;
  var c;
  for (i = 0; i < ca.length; i++) {
    c = ca[i];
    while (c.charAt(0) === ' ') {
      c = c.substring(1, c.length);
    }
    if (c.indexOf(nameEQ) === 0) {
      return c.substring(nameEQ.length, c.length);
    }
  }
  return null;
};

/**
 * Creates a new timer which redirects the user if the `loggedout` cookie is
 * set.
 *
 * url: The url to redirect to.
 **/
utils.logoutTimer = function readCookie(url) {
  if (!timer) {
    if (loggedin) {
      // We were logged in when this was called. Set up our logout timer.
      timer = window.setInterval(function redirect() {
        // if we are logged out and not already on the home page
        // If the loggedout cookie is set, a log out was initiated by the
        // user via.
        // If the exp cookie is missing, the user's session has expired.
        if ((utils.readCookie('loggedout') && window.location.pathname !== url) ||
            ((!utils.readCookie('exp')) && (window.location.pathname !== url))) {
          window.location.assign(url);
        }

      }, 500);
    }
  } else {
    window.clearInterval(timer);
  }
};

utils.setCookie = function(name, value, days) {
  var expires;
  if (days) {
    var date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    expires = '; expires=' + date.toGMTString();
  } else {
    expires = '';
  }

  document.cookie = name + '=' + value + expires + '; path=/';
};


$(window).ready(function () {
    if (typeof tools_companies !== 'undefined') {
        get_companies();
    }

    $.each($('li.mobile-trigger'), function(i) {
      var self = $(this);
      var currentListItem = self.children('.mobile-submenu').children('.mobile-sub-nav');
      currentListItem.on('click', function(e) {
        e.stopPropagation();
      });

      self.on('click', function(e) {
        e.stopPropagation();
        $('.mobile-submenu').children('.mobile-sub-nav').not(currentListItem).removeClass('mobile-list-open');
        currentListItem.toggleClass('mobile-list-open');
        if($('.mobile-submenu').children('.mobile-sub-nav').hasClass('mobile-list-open')){
        $('.overlay').show();
        $('body').addClass('no-scroll');
      }else{
        $('.overlay').hide();
        $('body').removeClass('no-scroll');
      }
      });
    });

    //Javascript for closing the mobile menu on click of anywhere on the screen
    $(window).click(function() {
      var mobileSubContent = $('li.mobile-trigger').children('.mobile-submenu').children('.mobile-sub-nav');
      $.each(mobileSubContent, function(i) {
        var self = $(this);
        if(self.hasClass('mobile-list-open')){
          self.removeClass('mobile-list-open');
          $('body').removeClass('no-scroll');
          $('.overlay').hide();
        }
      });
    });

});

function get_companies() {
    // Function builds multiple company elements and functions
    var parent_list_item = document.createElement("li");
    parent_list_item.setAttribute("id", "current-company");
    parent_list_item.setAttribute("class", "submenu-dropdown");

    $(parent_list_item).bind("click", function (event) {
        event.preventDefault();
        var li_last_child = parent_list_item.lastChild;

        if (li_last_child.currentStyle ? li_last_child.currentStyle.display : getComputedStyle(li_last_child, null).display === "none")
            li_last_child.style.display = "block";
        else
            li_last_child.style.display = "none";
    });

    var label = document.createElement("a");
    // Company id from myjobs_company cookie
    var cid = utils.readCookie("myjobs_company");
    var list = document.createElement("ul");
    list.setAttribute("id", "select_company");

    // Company name used to show user what current company is selected
    var menu_company_name;
    var company_not_found = false;

    // Creating li items for "select_company" ul
    for (var i = 0; i < tools_companies.length; i++) {
        var company = tools_companies[i];

        // Get company name from cid, if cid exists
        if (!menu_company_name) {
            if (cid) {
                if (company.id == cid) {
                    menu_company_name = company.name;
                    company_not_found = false;
                } else {
                    company_not_found = true;
                }
            } else {
                set_cookie(tools_companies[0].id, 14);
                menu_company_name = tools_companies[0].name;
            }
        }

        var list_item = document.createElement("li");
        list_item.setAttribute("id", "company_" + String(company.id));
        list_item.innerHTML = "<a>" + company.name + "</a>";
        list_item.onclick = function () {
            var item_id = this.id.split("_")[1];

            // 14 = 2 weeks
            set_cookie(item_id, 14);

            // replaces text of main li holding company list
            parent_list_item.firstChild.innerHTML = "<strong>" + this.firstChild.innerHTML + "</strong>";

            process_reload();
        };
        list.appendChild(list_item);
    }

    if (company_not_found) {
        set_cookie(tools_companies[0].id, 14);
        menu_company_name = tools_companies[0].name;
    }

    label.innerHTML = menu_company_name + ' <span class="caret"></span>';
    parent_list_item.appendChild(label);
    parent_list_item.appendChild(list);

    var parent_element = document.getElementById("employer-apps"),
        first_child = parent_element.firstChild;
    parent_element.insertBefore(parent_list_item, first_child);

    // ---- Mobile ---- //
    var mobile_parent_list_item = document.createElement("li"),
        mobile_link = document.createElement("a");
    mobile_parent_list_item.setAttribute("id", "mobile-parent-company-list");
    mobile_parent_list_item.setAttribute("class", "mobile-sub-nav");
    // This is for the toggling of Employers list of companies
    $(mobile_parent_list_item).bind("click", function (event) {
        event.preventDefault();
        var mobile_li_last_child = mobile_parent_list_item.lastChild;

        if (mobile_li_last_child.currentStyle ? mobile_li_last_child.currentStyle.display : getComputedStyle(mobile_li_last_child, null).display === "none")
            mobile_li_last_child.style.display = "block";
        else
            mobile_li_last_child.style.display = "none";
    });

    mobile_link.innerHTML = "<strong><span class='glyphicon glyphicon-triangle-bottom'></span> " + menu_company_name + "</strong>";
    mobile_parent_list_item.appendChild(mobile_link);

    var pop_menu = document.getElementById("mobile-employer-apps");
    pop_menu.appendChild(mobile_parent_list_item);

    var mobile_list = document.createElement("ul");
    mobile_list.setAttribute("id", "mobile_select_company");
    mobile_parent_list_item.appendChild(mobile_list);

    for (var j = 0; j < tools_companies.length; j++) {
        var mobile_list_item = document.createElement("li");
        mobile_list_item.setAttribute("id", "mobilecompany_" + tools_companies[j].id);
        mobile_list_item.innerHTML = "<a>"+ tools_companies[j].name +"</a>";
        mobile_list_item.onclick = function() {
            var mobile_item_id = this.id.split("_")[1];
            set_cookie(mobile_item_id, 14);
            mobile_parent_list_item.firstChild.innerHTML = "<strong>"+ this.firstChild.innerHTML + "</strong>";
            process_reload();
        };
        mobile_list.appendChild(mobile_list_item);
    }
}

function process_reload() {
    /*
     Looks at what path the user is currently in.  If the path is showing
     an app that changing company matters redirect the user to a desired
     location instead of causing a 404.
     */
    var path = window.location.pathname,
        // Apps that changing company IDs would be a problem.
        // Despite being removed from navigation, candidates is still in
        // this list to allow changing of company on the now-delisted page.
        app_names = ["candidates", "prm", "posting"],
        new_href = window.location.protocol + "//" + window.location.host,
        app_name,
        i;

    for (i = 0; i < app_names.length; i++) {
        app_name = app_names[i];
        if (path.indexOf(app_name) !== -1) {
            if (app_name === "candidates") {
                // window.location.href used instead of window.location.replace
                // to simulate a link instead of a redirect.
                window.location.href = new_href + "/candidates/view/";

                // Return false so code doesn't reach location.reload() as it
                // was causing race conditions
                return false
            }
            else if (app_name === "prm") {
                window.location.href = new_href + "/prm/view/";
                return false
            }
            else if (app_name === "posting") {
                window.location.href = new_href + "/posting/admin/";
                return false
            }
        }
    }
    location.reload();
}

function set_cookie(company_id, days) {
    var expires;
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toGMTString();
    } else
        expires = "";
    document.cookie = "myjobs_company=" + company_id + expires + "; path=/";
}

function delete_cookie() {
    set_cookie("", -1);
}
