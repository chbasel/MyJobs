$(document).ready(function() {
    if($('[id$="url"]').val() == ""){
        disable_fields();
    } else {
        show_dates();
    }
    add_refresh_btn();
    $('[id$=notes]').placeholder();
    $('[id$="account_activation_message"]').hide();
    $('label[for$="account_activation_message"]').hide();
});


$(function() {
    $("[id$='_search']").on("click", function(e) {
        e.preventDefault();

        var form = $('#saved-search-form');

        var data = form.serialize();
        data = data.replace('=on','=True').replace('=off','=False');
        data = data.replace('undefined', 'None');
        $.ajax({
            data: data,
            type: 'POST',
            url: '/saved-search/view/save/',
            success: function(data) {
                if (data == '') {
                    window.location = '/saved-search/view/';
                } else {
                    add_errors(data);
                }
            }
        });
    });

    $(".refresh").on("click", function(e) {
        validate(e);
    });

    $("input[id$='url']").on("input keypress cut paste", function(e) {
        validate(e);
    });

    $('#id_email').on("change", function(e) {
        var csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
        var user_email = $('#id_email').val();
        verifying_contact('validating...');
        $.ajax({
            type: "POST",
            url: "/prm/view/searches/verify-contact/",
            data: { csrfmiddlewaretoken: csrf_token,
                    action: "validate",
                    email: user_email},
            success: function(data) {
                var json = jQuery.parseJSON(data);
                var status = json.status;
                var message = json.message;
                var help_span = $('#id_email').next().next();
                if(status == 'verified' || status == 'None') {
                    verifying_contact(status);
                    show_hide_content('hide');
                    help_span.text(message);
                } else {
                    verifying_contact(status);
                    show_hide_content('show');
                    help_span.text(message);
                }
            }
        });
    });

    $('[id$="partner_ss_save"]').on("click", function(e) {
        // interrupts default functionality of the button with code below
        e.preventDefault();

        var form = $('#partner-saved-search-form');
        var serialized_data = form.serialize();

        var company_id = $('[name=company]').val();
        var partner_id = $('[name=partner]').val();

        $.ajax({
            type: 'POST',
            url: '/prm/view/searches/save',
            data: serialized_data,
            success: function(data, status) {
                if(data == '') {
                    if(status != 'prevent-redirect') {
                        window.location = '/prm/view/searches?partner=' + partner_id;
                    }
                } else {
                    // form was a json-encoded list of errors and error messages
                    var json = jQuery.parseJSON(data);

                    // remove color from labels of current errors
                    $('[class*=required]').parent().prev().removeClass('error-text');

                    // remove current errors
                    $('[class*=required]').children().unwrap();

                    if($.browser.msie){
                        $('[class*=msieError]').remove()
                    }

                    for (var index in json) {
                        var $error = $('[id$="_'+index+'"]');
                        var $labelOfError = $error.parent().prev();

                        // insert new errors after the relevant inputs
                        $error.wrap('<div class="required" />');
                        $error.attr("placeholder",json[index][0]);
                        $error.val('')
                        $labelOfError.addClass('error-text');
                    }
                }
            }
        });
    });

    $('[id$="frequency"]').on("change", function() {
        show_dates();
    });
});


function validate(e) {
    if (e.target == $('[id$="url"]').get(0)) {
        if (this.timer) {
            clearTimeout(this.timer);
        }
        var pause_interval = 1000;
        // Take a little longer due to mobile requiring a keyboard
        // to come up onto screen, change keyboard views, ect.
        if($(window).width() < 500){
            pause_interval = 3000;
        }
        this.timer = setTimeout(function() {
            do_validate();
        }, pause_interval);
    } else {
        do_validate();
    }
}

function do_validate() {
    var csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    var url = $('[id$="url"]').val();
    validation_status('validating...')
    $.ajax({
        type: "POST",
        url: "/saved-search/view/validate-url/",
        data: { csrfmiddlewaretoken: csrf_token,
                action: "validate",
                url: url},
        success: function(data) {
            var json = jQuery.parseJSON(data);
            if (json.url_status == 'valid') {
                validation_status(json.url_status);
                if ($('[id$="label"]').val().length == 0) {
                    $('[id$="label"]').val(json.feed_title);
                }
                if ($('[id$="feed"]').val() != json.rss_url) {
                    $('[id$="feed"]').val(json.rss_url);
                }
                enable_fields();
                show_dates();

            }
            else {
                validation_status(json.url_status);
                disable_fields();
            }
        }
    });
}

function validation_status(status) {
    var label_text;

    if (status == 'valid') {
        label_text = 'label-success';
    } else {
        label_text = 'label-important';
    }
    if ($('#validated').length) {
        $('#validated').removeClass('label-success');
        $('#validated').removeClass('label-important');
        $('#validated').addClass(label_text);
        $('#validated').text(status);
    } else {
        var url_div = $('[id$="url"]').parent();
        var desired_location = url_div.next();
        desired_location.after('<div class="span3 form-label pull-left initial">&nbsp;</div>'+
            '<div class="profile-form-input"><div id="validated" class="label '+
            label_text+' prm-valid">'+status+'</div></div>'+
            '<div class="clear"></div>');
    }
}

function verifying_contact(status) {
    var verified_label;
    if(status == "verified") {
        verified_label = 'label-success';
    } else {
        verified_label = 'label-important';
    }
    var email_div = $('#id_email');
    if($('#verified-contact').length) {
        var vc = $('#verified-contact');
        vc.removeClass('label-success');
        vc.removeClass('label-important');
        vc.addClass(verified_label);
        vc.text(status);
        email_div.css('width', calc_select_width(vc.outerWidth()))

    } else {
        email_div.after('<div id="verified-contact" class="label '+
            verified_label+' prm-valid pull-right">'+status+'</div>');
        var vc = $('#verified-contact');
        vc.css({'margin-top': '3px', 'margin-bottom': '0px'});
        email_div.css('width', calc_select_width(vc.outerWidth()))
    }
    if(status == "None") {
        if ($(document).width() > 500) {
            email_div.css('width', 262);
        } else {
            email_div.css('width', '100%');
        }
        vc.remove();
    }
}

function calc_select_width(label_width) {
    var email_div = $('id_email');
    if ($(document).width() > 500) {
        return 262 - label_width - 5;
    } else {
        email_div.css('width', '100%');
        return email_div.width() - label_width - 5;
    }
}


function show_hide_content(status) {
    if(status == 'hide'){
        $('[id$="account_activation_message"]').hide();
        $('label[for$="account_activation_message"]').hide();
    } else {
        $('[id$="account_activation_message"]').show();
        $('label[for$="account_activation_message"]').show();
    }
}


function add_refresh_btn() {
    var url_field = $('#id_url'),
        field_width = $('#id_label').width(); 

    url_field.parent().addClass('input-append');
    url_field.after('<span class="btn add-on refresh"><i class="icon icon-refresh">');
    url_field.width(field_width - $('span.refresh').outerWidth());
}

function show_dates(){
    if ($('[id$="frequency"]').attr('value') == 'D') {
        $('label[for$="day_of_month"]').hide();
        $('label[for$="day_of_week"]').hide();
        $('[id$="day_of_month"]').hide();
        $('[id$="day_of_week"]').hide();
    } else if ($('[id$="frequency"]').attr('value') == 'M') {
        $('label[for$="day_of_week"]').hide();
        $('label[for$="day_of_month"]').show();
        $('[id$="day_of_week"]').hide();
        $('[id$="day_of_month"]').show();
    } else if ($('[id$="frequency"]').attr('value') == 'W') {
        $('label[for$="day_of_month"]').hide();
        $('label[for$="day_of_week"]').show();
        $('[id$="day_of_month"]').hide();
        $('[id$="day_of_week"]').show();
    }
}

function disable_fields() {
    $('[id$="url_extras"]').hide();
    $('label[for$="url_extras"]').hide();
    $('[id$="is_active"]').hide();
    $('label[for$="is_active"]').hide();
    $('[id$="email"]').hide();
    $('label[for$="email"]').hide();
    $('[id$="account_activation_message"]').hide();
    $('label[for$="account_activation_message"]').hide();
    $('[id$="frequency"]').hide();
    $('label[for$="frequency"]').hide();
    $('[id$="notes"]').hide();
    $('label[for$="notes"]').hide();
    $('[id$="day_of_week"]').hide();
    $('label[for$="day_of_week"]').hide();
    $('[id$="day_of_month"]').hide();
    $('label[for$="day_of_month"]').hide();
    $('[id$="partner_message"]').hide();
    $('label[for$="partner_message"]').hide();
    $('[class*="help-block"]').hide();
    $('.primary').hide();
    $('label[for$="p-tags"]').hide();
    $('ul.tagit').hide();
}

function enable_fields() {
    $('[id$="url_extras"]').show();
    $('label[for$="url_extras"]').show();
    $('[id$="is_active"]').show();
    $('label[for$="is_active"]').show();
    $('[id$="email"]').show();
    $('label[for$="email"]').show();
    $('[id$="frequency"]').show();
    $('label[for$="frequency"]').show();
    $('[id$="notes"]').show();
    $('label[for$="notes"]').show();
    $('[id$="day_of_week"]').show();
    $('[id$="day_of_month"]').show();
    $('label[for$="day_of_week"]').show();
    $('label[for$="day_of_month"]').show();
    $('[id$="partner_message"]').show();
    $('label[for$="partner_message"]').show();
    $('[class*="help-block"]').show();
    $('.primary').show();
    $('label[for$="p-tags"]').show();
    $('ul.tagit').show();
}
