function drawChart() {
    var company_id = $('#company').val();
    var partner_id = $('#partner').val();
    $.ajax({
        type: "GET",
        data: {company: company_id,
               partner: partner_id,
               type: 'sample'},
        url: "/prm/view/records/retrieve_records",
        success: function(dump){
            var nums = jQuery.parseJSON(dump);
            var data = google.visualization.arrayToDataTable([
                            ['Records',         'All Records'],
                            ['Email',           nums.email],
                            ['Phone Calls',     nums.phone],
                            ['Face to Face',    nums.facetoface]
                        ]);
            var options = donut_options(200, 200, 12, 12, 175, 175, 0.6);
            var chart = new google.visualization.PieChart(document.getElementById('donutchart'));
            chart.draw(data, options);
            fill_piehole(nums.totalrecs);
            visual_boxes(nums.email, nums.phone, nums.facetoface);
        }
    });
}

function donut_options(height, width, chartArea_top, chartArea_left, chartArea_height, chartArea_width, piehole_radius){
    var options = {
                    legend: 'none',
                    pieHole: piehole_radius,
                    pieSliceText: 'none',
                    height: height,
                    width: width,
                    chartArea: {top:chartArea_top, left:chartArea_left, height: chartArea_height, width: chartArea_width},
                    slices: {0: {color: '#5eb95e'}, 1: {color: '#4bb1cf'}, 2: {color: '#faa732'}}
                  };
    return options
}

function fill_piehole(totalrecs){
    var doughnut = $("#donutchart");
    var piediv = doughnut.children(":first-child").children(":first-child");
    piediv.prepend('<div class="piehole"><div class="piehole-big">'+String(totalrecs)+'</div><div class="piehole-topic">Contact Records</div><div class="piehole-filter">30 Days</div></div>');
}

function visual_boxes(email, phone, facetoface){
    var record_types = new Array(facetoface, phone, email);
    var readable_phone; var readable_email;

    // Pluralization
    if(phone === 1){readable_phone = 'Phone Call'} else {readable_phone = 'Phone Calls'}
    if(email === 1){readable_email = 'Email'} else {readable_phone = 'Emails'}
    var readable_types = new Array('Face to Face', readable_phone, readable_email);

    var doughnut = $("#donutchart");
    for(var i in readable_types){
        doughnut.prepend('<div class="chart-box"><div class="big-num">'+String(record_types[i])+'</div><div class="reports-record-type">'+readable_types[i]+'</div></div>');
    }
}
