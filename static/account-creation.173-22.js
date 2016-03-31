var current_url = ""; //init current_url as global
var profile_url = "/profile/";
$(document).ready(function() {
    $( "input[id$='date']" ).datepicker({dateFormat: window.dateFormat,
                                                     constrainInput: false});

    // perform display modifications for fields on initial profile form
    $("#newAccountData #id_name-primary").hide()
    $("#newAccountData label[for=id_name-primary]").hide()
    current_url = '/';
    rotate_tagline();
});

function rotate_tagline(){
    /*
    Rotates the tagline target audience keyword.

    Inputs: none
    Returns: none (DOM manipulation)
    */
    var tagline = $('#tagline a'),
        phrases = ["Compliance",
                   "Jobs",
                   "Employers",
                   "Diversity",
                   "Veterans"],
        fadeDuration = 1500,
        random_phrases = shuffle(phrases),
        loop = function(index, list) {
            if(index == list.length) return false;

            tagline.fadeOut(fadeDuration/5, function() {
                tagline.html(list[index]);
            })
                .fadeIn(fadeDuration, function() {
                    loop(index + 1, list);
                });
        };

    tagline.html(random_phrases[0]);
    tagline.fadeIn('fast');
    var selected_phrases = random_phrases.slice(0,3);
    selected_phrases[selected_phrases.length] = "You.";
    setTimeout(function() {
        loop(1, selected_phrases);
    }, fadeDuration);
}

function shuffle(list) {
    /*
    Fisher-Yates Shuffle

    Inputs:
    :list:      The source array

    Returns:
    :list:      A randomized array
     */
    var i = list.length;
    if(i == 0) return false;
    while(--i) {
        var j = Math.floor( Math.random() * (i + 1) ),
            tempi = list[i],
            tempj = list[j];
        list[i] = tempj;
        list[j] = tempi;
    }
    return list;
}

/* When register button is clicked, this triggers an AJAX POST that sends the
   csrf token, the collected email and password fields, and a custom field, 'action'
   that allows the view to differentiate between different AJAX requests.
*/
$(document).on("click", "button#register", function(e) {
    e.preventDefault();
    csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    var form = $('form#registration-form');
    form.children('.form-error').remove();
    var json_data = form.serialize()+'&action=register&csrfmiddlewaretoken='+csrf_token;
    user_email = $("#id_email").val();
    $.ajax({
        type: "POST",
        url: current_url,
        data: json_data,
        global: false,
        success: function(data) {
            /*
            The output in this data is a little different than the rest.
            This one outputs errors, when there are errors. But on success,
            outputs a gravatar url, instead of 'valid' or 'success'.
            */
            var json = jQuery.parseJSON(data);
            if (json.success === true){
              window.location.assign('/profile/view/');
            } else{
                // Remove all required field changes, if any
                removeRequiredChanges();

                // '__all__' refers to validation errors raised in the general
                // Django forms clean() method. Specific methods, like
                // clean_password1(), would place their error messages in
                // 'password1', for instance.
                var search = '__all__';

                // Does this form contain generic clean() errors?
                var formErrors = false;

                $.each(json.errors, function(index, value){
                    $.each(value[1], function(key, cell){
                        if (search === value[0]) {
                            var error = json.errors[index][1];
                            if (error[0] !== "") {
                                form.prepend("<div class='form-error'>"+error+"</div>");
                                formErrors = true;
                            }
                        }
                    });
                });
                if (!formErrors) {
                    // For every error passed by json, run jsonError function
                    for (var index in json.errors) {
                        jsonErrors(index, json.errors);
                    }
                }

            }
        }
    });
});

$(document).on("click", "button#login", function(e) {
    e.preventDefault();
    removeRequiredChanges();
    var next = document.getElementsByName('next')[0].value;
    var form = $('form#login-form');
    var json_data = form.serialize()+'&nexturl='+next+'&action=login';
    $.ajax({
        type: "POST",
        url: current_url,
        data: json_data,
        global: false,
        success: function(data) {
            // converts json to javascript object
            var json = jQuery.parseJSON(data);
            if (json.validation != 'valid') {
                // Remove all required field changes, if any
                removeRequiredChanges();

                // For every error passed by json, run jsonError function
                for (var index in json.errors) {
                    jsonErrors(index, json.errors);
                }
            } else {
                if(json.url == 'None'){
                    window.location = profile_url;
                }else{
                    window.location = json.url;
                }
            }
        }
    });
});

$(document).on("click", "button.activation-login", function(e) {
    e.preventDefault();
    var user_email = document.getElementById('user_email');
    var form = $('form#login-form');
    var json_data = form.serialize()+'&action=login';
    $.ajax({
        type: "POST",
        url: current_url,
        data: json_data,
        global: false,
        success: function(data) {
            // converts json to javascript object
            var json = jQuery.parseJSON(data);
            if (json.validation != 'valid') {
                // Remove all required field changes, if any
                removeRequiredChanges();

                // For every error passed by json, run jsonError function
                for (var index in json.errors) {
                    jsonErrors(index, json.errors);
                }
            } else {
                // perform the visual transition to page 2
                if (json.units === true){
                    window.location = profile_url
                } else if (json.success === true){
                    window.location.assign('/profile/view/');
                }
            }
        }
    });

});

$(document).on("click", "button#save", function(e) {
    e.preventDefault();
    csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    setPrimaryName();
    var form = $('form#profile-form');
    // replace on and off with True and False to allow Django to validate
    // boolean fields
    var json_data = form.serialize().replace('=on','=True')
        .replace('=off','=False')+'&action=save_profile&csrfmiddlewaretoken='+csrf_token;
    $.ajax({
        type: "POST",
        url: current_url,
        data: json_data,
        global: false,
        success: function(data) {
            if (data != 'valid') {
                form.replaceWith(data);
                $("#id_name-primary").hide()
                $("label[for=id_name-primary]").hide()
                $( "input[id$='date']" ).datepicker({dateFormat: window.dateFormat,
                                                 constrainInput: false});
            } else {
                window.location = profile_url;
            }
        }
    });
});

$(document).on("change", "#newAccountData", function() {
    // Calculates the profile completion level every time a field on
    // the new account profile form is changed.

    profile_completion = 0;
    if($("#id_name-given_name").val() != "" && $("#id_name-family_name").val() != "") {
        profile_completion += 1;
    }
    if($("#id_edu-organization_name").val() != "" && $("#id_edu-degree_date").val() != "" &&
       $("#id_edu-education_level_code").val() >= 3) {
        profile_completion += 1;
    }
    if ($("#id_ph-area_dialing").val() != "" || $("#id_ph-number").val() != "" ||
        $("#id_ph-extension").val() != "" || $("#id_ph-use_code").val() != "") {
        profile_completion += 1;
    }
    if ($("#id_addr-address_line_one").val() != "" || $("#id_addr-address_line_two").val() != "" ||
        $("#id_addr-city_name").val() != "" || $("#id_addr-country_sub_division_code").val() != "" ||
        $("#id_addr-country_code").val() != "" || $("#id_addr-postal_code").val() != "") {
        profile_completion += 1;
    }
    if($("#id_work-position_title").val() != "" && $("#id_work-organization_name").val() != "" &&
       $("#id_work-start_date").val() != "") {
        profile_completion += 1;
    }

    profile_completion = Math.round((profile_completion/num_modules)*100);

    bar = "bar ";
    if(profile_completion <= 20) {
        bar += "bar-danger";
    }
    else if(profile_completion <= 40) {
        bar += "bar-warning";
    }
    else if(profile_completion <= 60) {
        bar += "bar-info";
    }
    else {
        bar += "bar-success";
    }

    $("#initial-bar").removeClass();
    $("#initial-bar").addClass(bar);

    $("#initial-bar").css("width", profile_completion + "%");
    $(".initial-highlight").text(profile_completion + "% complete");
});

// go to next carousel div on click
$(document).on("click", "button#next", function(e) {
    e.preventDefault();
    $("#carousel").rcarousel("next");
});

// skip to profile page on click
$(document).on("click", "button#profile", function(e) {
    e.preventDefault();
    window.location = profile_url;
});

function setPrimaryName(){
    /**
    Detects if a value hasbeen entered in either name form and sets the hidden
    checkmark field for priamry to true (since this is the users only name
    at this point. This prevents false validation errors when the form is empty.
    **/
    first_name = $("#id_name-given_name").val();
    last_name = $("#id_name-family_name").val();
    if(first_name!=""||last_name!=""){
        $("#id_name-primary").attr("checked","checked");
    }else{
        $("#id_name-primary").attr("checked",false);
    }
}

function removeRequiredChanges(){
    $.each($(".required"), function( index, value ) {
        var thisHelpText = $(this).children().data("helptext");
        if (thisHelpText !== undefined){
            $(value).siblings('.error-text').replaceWith("<div class='helptext'>" + thisHelpText + "</div>");
        }
    });
    $(".required").contents().unwrap();
    $(".error-text").remove();
}

function jsonErrors(index, errors){
    /*
    Gets errors and adds front-end attributes and styling to show the user
    what went wrong with their form. Shows error messages in placeholders for
    browsers with the exception of IE. IE messages are displayed above the field
    that has the error.

    This function in most cases will be ran in conjunction with a for loop.

    :index:     Is an integer, comes from the iterated value from a for loop.
    :errors:    Parsed json that has the label "errors". Errors is a
                'multidimensional array' {errors:[key][value]}
    */

    var $error = $('#id_' + errors[index][0]);
    $error.wrap("<div class='required'></div>");

    // clear password fields on error
    if(errors[index][0].indexOf("password") != -1)
        $error.val("");
    // insert new errors after the relevant inputs
    $.each(errors[index][1], function(index, value){
        var value = "<div class='error-text'>" + value + "</div>";
        if ($error.parent().siblings('.helptext').length) {
            $error.data("helptext",$error.parent().siblings('.helptext').text())
            $error.parent().siblings('.helptext').replaceWith(value)
        } else if ($error.parent().siblings('.error-text').length) {
            $error.parent().siblings('.error-text').replaceWith(value)
        } else {
            $error.parent().after(value)
        }
    });
}
