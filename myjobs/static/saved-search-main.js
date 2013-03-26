$(document).ready(function() {
    check_digest_options();
    $('tr').click(function() {
        var href = $(this).find('.edit').prop('href');
        if ($(window).width() <= 500 && typeof(href) != 'undefined') {
            window.location = href;
        }
    });
    $('#new_btn').click(function(e) {
        e.preventDefault();
        $('#new_modal').modal();
    });
    $(window).resize(function() {
        var dW;
        var dH;
        if ($(window).width() <= 500) {
            dW = dH = 0;
        } else {
            dW = dH = 0.1;
        }
        console.log(dW + ' ' + dH);
        var width = $(window).width();
        var margin_w = width * dW;
        var height = $(window).height();
        var margin_h = height * dH;
        $('.modal-body').css('margin', margin_w+'px '+margin_h+'px;');
    });
});

function check_digest_options() {
    // When the user interacts with any fields in the Digest Options form,
    // an ajax request checks that the form is valid and saves the changes
    var timer;
    var pause_interval = 1000;

    $('#id_digest_email').keyup(function() {
        clearTimeout(timer);
        if (form_valid()) {
            timer = setTimeout(save_form, pause_interval);
        }
    });

    $('#id_digest_active').click(function() {
        if (form_valid()) {
            save_form();
        }
    });

    $('#id_send_if_none').click(function() {
        if (form_valid()) {
            save_form();
        }
    });

    function form_valid() {
        $('.digest_error').remove();
        var error;
        if ($('#id_digest_active').prop('checked')) {
            if ($('#id_digest_email').val().length) {
                return true;
            }
        }
        return false;
    }

    function form_status(status) {
        $('#saved').addClass('label label-info');
        $('#saved').text(status);
        $('#saved').fadeIn().fadeOut('slow');
    }

    function save_form() {
        var csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
        $.ajax({
            data: { csrfmiddlewaretoken: csrf_token, action: 'save',
                    is_active: $('#id_digest_active').prop('checked')? 'True':'False',
                    email: $('#id_digest_email').val(),
                    send_if_none: $('#id_send_if_none').prop('checked')? 'True':'False' },
            type: 'POST',
            url: '',
            success: function(data) {
                if (data == 'success') {
                    form_status('Saved!');
                } else {
                    form_status('Something went wrong');
                }
            }
        });

    }
};
