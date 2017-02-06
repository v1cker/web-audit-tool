$(document).ready(function(){
    var _name = 'n/a';
    var host = 'n/a';
    var sql = 0;
    var sql_blind = 0;
    var xss = 0;
    var file_upload = 0;
    var port_insecure = 0;
    var info = 0;
    var _total = 0;
    // 
    // save to pdf
    //
    var doc = new jsPDF('p', 'pt', 'letter');
    var specialElementHandlers = {
        '#editor': function (element, renderer) {
            return true;
        }
    };
    var pagesplit = {
         pagesplit: true
    };
    
    $('#save_to_pdf').click(function () {
        doc.fromHTML($('#form_save_to_pdf').html(), 15, 15, {
            'width': 1000,
            'elementHandlers': specialElementHandlers,
            pagesplit
        });
        
        doc.save(''+_name+'.pdf');

    });
    
    function _chart(name, host, sql, sql_blind, xss, file_upload, port_insecure, info) {
        _name = name +':'+ host
        //_total = sql + sql_blind + xss + file_upload;
        _sql = sql/_total;
        _sql_blind = sql_blind/_total;
        _xss = xss/_total;
        _file_upload = file_upload/_total;
        _port_insecure = port_insecure/_total;
        _info = info/_total;
        console.log(_total);
        console.log(_port_insecure);
        console.log(info);
        Highcharts.chart('chart', {

            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: 'pie'
            },
            title: {
                text: _name
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                        style: {
                            color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                        }
                    }
                }
            },
            series: [{
                name: 'Brands',
                colorByPoint: true,
                data: [{
                    name: 'XSS Injection',
                    y: _xss
                }, {
                    name: 'Blind SQL Injection',
                    y: _sql_blind,
                    sliced: true,
                    selected: true
                }, {
                    name: 'SQL Injection',
                    y: _sql
                }, {
                    name: 'File Upload',
                    y: _file_upload
                },{
                    name: 'Port Insecure',
                    y: _port_insecure
                },{
                    name: 'Info',
                    y: _info
                }]
            }]
        });
    };

    $('#scan').click(function() {
        //remove value
        
    	var list_scan = [];
    	var url = $('#url_scan').val();    	
        $.each($("input[type='checkbox']:checked"), function(){            
                list_scan.push($(this).val());
        });
        console.log(list_scan);
        console.log(url);

        if (list_scan.length == 0 || url == '' || url == null){
        	$('.error').text('Có lỗi xảy ra. Hãy thử lại!');
			$('.error').show();

        	return;
        }else{
        	$('.error').text('')
        	$('.error').hide();

        	$.ajax({
	            type: "post",
				contentType: "application/json; charset=utf-8",
	            url: "http://localhost:5050/scan",
	           
                data: JSON.stringify({ "list_scan": list_scan, "url": url}),
                dataType: "json",
                success: function(data){
                    
                    var result = data.result;
                    console.log(result);
                    $.each(result, function( key, value ) {
                        if (key == 'info'){
                            info = value.total;
                            name = value.domain;
                            host = value.host;
                            console.log(value);                            
                            $('#start_date').text(value.string_start);
                            $('#end_date').text(value.string_end);
                            $('#duration').text(value.duration+' s');
                            $('#domain').text(value.domain);
                            $('#host').text(value.host);
                            $('#server').text(value.server_url);
                            $('#x_powered_by').text(value.x_powered_url);

                        } // end if info
                        if (key == 'sql'){
                            sql = value.total_vul;
                            _total += value.total_vul;
                            $('#detail').append("<div id ='rs_sql'>\
                                <br><a href='#sql' data-toggle='collapse'>SQL Injection <span class='badge' id='num_sql'>"
                                +value.total_vul+
                                "</span></a><br>\
                                </div>\
                                <div id='sql' class='collapse result_sql'><br>\
                                "
                                );
                            $('.result_sql').append("<p class='#num_sql'>Numbers: "+value.total_vul+"</p>");
                            if (value.url.level != ''){
                                $('.result_sql').append("<p>URL: </p>");
                                $('.result_sql').append("<p class='level level_sql_url "+value.url.level+"'>Level: "+value.url.level+"</p>");
                                $('.result_sql').append("<p class='detail detail_sql_url'></p>");

                                $.each(value.url.list,function(index,sql_url){                                
                                    $('.result_sql .detail_sql_url').append("<pre><code>"+sql_url+"</code></pre>");
                                });
                            }
                            if (value.form.level != ''){
                                $('.result_sql').append("<p>FORM: </p>");
                                $('.result_sql').append("<p class='level level_sql_form "+value.form.level+"'>Level: "+value.form.level+"</p>");
                                $('.result_sql').append("<p class='detail detail_sql_form'></p>");                                
                                $.each(value.form.url,function(index,form_url){                                
                                        $('.result_sql .detail_sql_form').append("<pre><code>"+form_url+"</code></pre>");
                                });  
                                $.each(value.form.list,function(index,sql_form){                                
                                        $('.result_sql .detail_sql_form').append("<pre><code>"+sql_form+"</code></pre>");
                                });
                            }
                            $('.result_sql').append("<br>");

                        } //end if sql
                        if (key == 'sql_blind'){
                            sql_blind = value.total_vul;
                            _total += sql_blind;
                            $('#detail').append("<div id ='rs_sql_blind'>\
                                <br><a href='#sql_blind' data-toggle='collapse'>Blind SQL Injection <span class='badge' id='num_sql_blind'>"
                                +value.total_vul+
                                "</span></a><br>\
                                </div>\
                                <div id='sql_blind' class='collapse result_sql_blind'><br>\
                                "
                                );
                            $('.result_sql_blind').append("<p class='#num_sql_blind'>Numbers: "+value.total_vul+"</p>");
                            if (value.url.level != ''){
                                $('.result_sql_blind').append("<p>URL: </p>");
                                $('.result_sql_blind').append("<p class='level level_sql_blind_url "+value.url.level+"'>Level: "+value.url.level+"</p>");
                                $('.result_sql_blind').append("<p class='detail detail_sql_blind_url'></p>");

                                $.each(value.url.list,function(index,sql_url){                                
                                    $('.result_sql_blind .detail_sql_blind_url').append("<pre><code>"+sql_url+"</code></pre>");
                                });
                            }
                            if (value.form.level != ''){
                                $('.result_sql_blind').append("<p>FORM: </p>");
                                $('.result_sql_blind').append("<p class='level level_sql_blind_form "+value.form.level+"'>Level: "+value.form.level+"</p>");
                                $('.result_sql_blind').append("<p class='detail detail_sql_blind_form'></p>");
                                $.each(value.form.url,function(index,form_url){                                
                                        $('.result_sql_blind .detail_sql_blind_form').append("<pre><code>"+form_url+"</code></pre>");
                                });  
                                $.each(value.form.list,function(index,sql_form){                                
                                        $('.result_sql_blind .detail_sql_blind_form').append("<pre><code>"+sql_form+"</code></pre>");
                                });
                            }
                            $('.result_sql_blind').append("<br>");

                        } //end if sql_blind
                        if (key == 'xss'){
                            //
                            // xss_stored
                            //
                            xss = value.total_vul;
                            _total = xss;
                            $('#detail').append("<div id ='rs_xss'>\
                                <br><a href='#xss' data-toggle='collapse'>XSS Injection <span class='badge' id='num_xss'>"
                                +value.total_vul+
                                "</span></a><br>\
                                </div>\
                                <div id='xss' class='collapse result_xss'><br>\
                                "
                                );
                            if (value.xss_s.total > 0){
                                $('.result_xss').append("<p>XSS Stored: </p>");
                                $('.result_xss').append("<p class='#num_stored_xss'>Numbers: "+value.xss_s.total+"</p>");
                                $('.result_xss').append("<p class='level level_xss_stored "+value.xss_s.level+"'>Level: "+value.xss_s.level+"</p>");
                                $('.result_xss').append("<p class='detail detail_xss_stored'></p>");
                                $.each(value.xss_s.url,function(index,xss_url){                                
                                        $('.result_xss .detail_xss_stored').append("<pre><code>"+xss_url+"</code></pre>");
                                });
                                $.each(value.xss_s.form,function(index,xss_form){                                
                                        $('.result_xss .detail_xss_stored').append("<pre><code>"+xss_form+"</code></pre>");
                                });
                            }
                            $('.result_xss').append("<br>");
                            //
                            // xss_ref
                            //
                            if (value.xss_r.total > 0){
                                $('.result_xss').append("<p>XSS Reflected: </p>");
                                $('.result_xss').append("<p class='#num_xss_reflected'>Numbers: "+value.xss_r.total+"</p>");
                                $('.result_xss').append("<p class='level level_xss_reflected "+value.xss_r.level+"'>Level: "+value.xss_r.level+"</p>");
                                $('.result_xss').append("<p class='detail detail_xss_reflected'></p>");                          
                                $.each(value.xss_r.url,function(index,xss_url){                                
                                        $('.result_xss .detail_xss_reflected').append("<pre><code>"+xss_url+"</code></pre>");
                                });
                                $.each(value.xss_r.form,function(index,xss_form){                                
                                        $('.result_xss .detail_xss_reflected').append("<pre><code>"+xss_form+"</code></pre>");
                                });
                            }
                            $('.result_xss').append("<br><br>");
                            
                        } // end if xss
                        if (key == 'file_upload'){
                            file_upload = value.total_vul;
                            _total = file_upload;
                            $('#detail').append("<div id ='rs_file_upload'>\
                                <br><a href='#file_upload' data-toggle='collapse'>File Upload <span class='badge' id='num_file_upload'>"
                                +value.total_vul+
                                "</span></a><br>\
                                </div>\
                                <div id='file_upload' class='collapse result_file_upload'><br>\
                                "
                                );
                            if (value.total_vul > 0){
                                $('.result_file_upload').append("<p class='#num_file_upload_form'>Numbers: "+value.total_vul+"</p>");
                                $('.result_file_upload').append("<p class='level level_file_upload_form "+value.form.level+"'>Level: "+value.form.level+"</p>");
                                $('.result_file_upload').append("<p class='detail detail_file_upload_form'></p>");
                                $.each(value.url.list,function(index,file_url){                                
                                        $('.result_file_upload .detail_file_upload_form').append("<pre><code>"+file_url+"</code></pre>");
                                });
                                $.each(value.form.list,function(index,file_form){                                
                                        $('.result_file_upload .detail_file_upload_form').append("<pre><code>"+file_form+"</code></pre>");
                                });
                            }
                            $('.result_xss').append("<br>");
                        } // end if port
                        if (key == 'port'){
                            port_insecure = value.info.total_insecure;
                            info += value.info.total_secure;
                            _total += value.info.total_insecure;
                            _total += value.info.total_secure;
                            $('#detail').append("<div id ='rs_port'>\
                                <br><a href='#port' data-toggle='collapse'>Port <span class='badge' id='num_port'>"
                                +value.info.total_insecure+
                                "</span></a><br>\
                                </div>\
                                <div id='port' class='collapse result_port'><br>\
                                "
                                );
                            //
                            // port secure
                            //
                            $('.result_port').append("<p>Port Secure: </p>");
                            $('.result_port').append("<p class='#num_port_secure'>Numbers: "+value.info.total_secure+"</p>");
                            $('.result_port').append("<p class='level level_port_secure info'>Level: Info</p>");
                            if (value.info.total_secure > 0){
                                $('.result_port').append("<p class='detail detail_port_secure'></p>");
                                $.each(value.detail.secure,function(index,secure){                                
                                    $('.result_port .detail_port_secure').append("<pre><code>"+secure.port+" - "+secure.name+"</code></pre>");
                                });
                            }
                            //
                            // port insecure
                            //
                            $('.result_port').append("<p>Port Insecure: </p>");
                            $('.result_port').append("<p class='#num_port_insecure'>Numbers: "+value.info.total_insecure+"</p>");
                            $('.result_port').append("<p class='level level_port_insecure "+value.level.insecure+"'>Level: "+value.level.insecure+"</p>");
                            if (value.info.total_insecure > 0){
                                $('.result_port').append("<p class='detail detail_port_insecure'></p>");
                                $.each(value.detail.insecure,function(index,insecure){                                
                                    $('.result_port .detail_port_insecure').append("<pre><code>"+insecure.port+" - "+insecure.name+"</code></pre>");
                                });
                            }
                        } // end if ssl
                        if (_total > 0 ){
                            _chart(name, host, sql, sql_blind, xss, file_upload, port_insecure, info);
                        }

                    });
                } ,
                error: function( jqXhr, textStatus, errorThrown ) {
                    console.log(errorThrown);
                }
            });
        
        }
        
    });
    
});
