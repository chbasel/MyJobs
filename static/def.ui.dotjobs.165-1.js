$(document).ready(function(){
    // Ensure site_name is defined and page isn't using secure blocks for
    // topbar
    if(typeof site_name != 'undefined' &&
    !$("*[data-widget_type=tools]").length) {
        get_toolbar(site_name);
    }


    $(".imageControl").click(function(){
        node = $(this).attr("data-node"); 
        rotateBillboardImage(node);
    });    
    $(".copyrightControl").click(function(){toggleCopyright($(this));});
    $("#direct_dotjobsIconBar .browse").click(function(){
        var imageStr = "";
        direction=1;
        if($(this).hasClass("prev")){
            direction = -1;    
        }
        for(var i=1;i<8;i++){
            if(direction<0){
                anchorLogo = leftLogo;
            }else{
                anchorLogo = rightLogo;
            }                
            node = anchorLogo+(i*direction);
            
            if(node<0){
                node=companyLogoCount+node+1;
            }
            else if(node>companyLogoCount){
                node=companyLogoCount-node;
            }
            node=Math.abs(node);            
            if(i==7){
                leftLogo+=7*direction;
                rightLogo+=7*direction;
            }
            newImage ='<a href="'+companyLogos[node].url;
            newImage+='/" class="icon"><img src="//d2e48ltfsb5exy.cloudfront.net/100x50/logo.gif"';
            newImage+=' style="background-image: url('+companyLogos[node].image+')"';
            newImage+=' alt="'+companyLogos[node].name+' Careers"/></a>';
            if(direction>0){
                imageStr += newImage;
            }else{
                imageStr = newImage+imageStr;
            }
        }
        var slideDirection = "right";
        if(direction==-1){slideDirection = "left";}            
        $("#direct_dotjobsIconContainer").hide();
        $("#direct_dotjobsIconContainer").html(imageStr);
        $("#direct_dotjobsIconContainer").fadeIn(500);            
    });
    /*
    Filter Carousel
    */
    var filterBoxCount = 0;
    var filterGroupCount = 0;
    var currentFilterBox = 1;
    var currentFilterGroup = 1;
    $(".direct_dotjobsFilterContainer").each(function(){
        filterBoxCount++;
        if(filterBoxCount%3==0){
            filterGroupCount++;     
        }
    })
    if(filterBoxCount%3>0){
        filterGroupCount++;
    }
    if(filterGroupCount>1){
        for(i=0;i<filterGroupCount;i++){
            aString = "<a id='filterPagingIndicator"+(i+1)+"'";
            if(i==0){
                aString+=" class='active'";
            }
            aString+="'></a>"
            $("#direct_dotjobsCarouselContainer .navi").append(aString);
        }
    }else{
        $("#direct_dotjobsFilterCarousel .right").hide();
    }
    if(filterBoxCount<4){
        $("#direct_dotjobsFilterCarousel .right").hide();
    }
    $("#direct_dotjobsFilterCarousel .browse").click(function(){
        direction=1;
        if($(this).hasClass("next")){
            direction = -1;
            currentFilterGroup++;
        }else{
            currentFilterGroup--;
        }
        var scrollDistance = $("#direct_dotjobsCarouselContainer").width();
        scrollDistance+=5;
        var scrollBox = $("#direct_dotjobsCarouselContainer .direct_scrollBox");
        currentScroll = scrollBox.css("left");
        if(currentScroll=="auto"){
            currentScroll=0;
        }else{
            currentScroll=currentScroll.substr(0,currentScroll.indexOf("px"));
        }
        currentScroll=parseInt(currentScroll);
        newScroll = (scrollDistance*direction)+currentScroll;
        scrollBox.css("left",newScroll+"px");
        currentFilterBox-=(direction*3);
        
        if(currentFilterGroup>=filterGroupCount){
            $("#direct_dotjobsFilterCarousel .right").hide();
        }else if(filterGroupCount>1){
            $("#direct_dotjobsFilterCarousel .right").show();
        }
        if (currentFilterGroup==1){
            $("#direct_dotjobsFilterCarousel .left").hide();
        }else if(filterGroupCount>1){
            $("#direct_dotjobsFilterCarousel .left").show();
        }
        $("#direct_dotjobsCarouselContainer .navi a").removeClass("active");
        $("#direct_dotjobsCarouselContainer .navi a#filterPagingIndicator"+currentFilterGroup).addClass("active");
    });
});

// Toggle Copyright function
function toggleCopyright(copyControl){
    /**
    Toggles the copyright information display for billboard images.
    Input:
        :copyControl": a DOM object that contains said copyright info. This
                       function manipulatesthe style properties of this object.
    Returns:
        None
    **/
    html = copyControl.html();
    if(!copyControl.hasClass("copyrightControlActive")){
        html = copyControl.attr("data-copyright");
        html+= "<br/><a href='"+copyControl.attr("data-source")+"'>"+copyControl.attr("data-source")+"</a>";
        copyControl.addClass("copyrightControlActive");            
    }else{
        html="&copy;";
        copyControl.removeClass("copyrightControlActive");
    }          
    copyControl.html(html);
}
/*
Billboard image functionality
*/
function WriteMobileSafeBillboard(list,flag,width,first_id){
    /**
    Only write out the billboard image HTML if the browser window
    is able to display it. 500px is the threshold for mobile, and
    there is no need to force a mobile user to download multiple,
    large image that they can never display.
    Inputs:
        :list: array containing the billboard data from django
        :flag: flag that denotes if the DOM has been modified
        :width: the width threshold for mobile 
        :first_id: id of the first image object to be displayed.
    Returns:
        :flag: final true/false state of flag variable.
    Writes:
        HTML to calling location or specificed location
        
    **/
    if(typeof(list[0].hotspots[0])!='undefined'){//build hotspots if they exist
        $("#direct_dotjobsMetaBoxSearch").after(
            buildHotSpotHTML(list[0].hotspots[0],0,0,true)
        )
    }
    BuildHotSpotFunction(); // assign click functions to mobile ad
    if(detectWidth()>mobile_width){ // default wide format layout
        document.write(BuildBillboard(list));
        BuildHotSpotFunction();
        flag=true; // boolean flag that prevent multiple writes of the billboard
        $("#direct_billboardImage_0").fadeIn();
        $("#direct_dotjobsMetaBoxSearch .hotspotparent_0").fadeIn();
        $("#mobile_hotspot").hide();
    }else{
        $(document).ready(function(){
            $(window).resize(function(){
                /**
                Utility function that listens to the resize event and writes the
                billboard html if the size goes beyond the width setting.
                Will only trigger once per page view.
                **/
                if(detectWidth()>width && !flag){
                    $("#standardSearch").before(BuildBillboard(list));
                    BuildHotSpotFunction();
                    flag=true;
                    $("#direct_billboardImage_0").fadeIn();
                    $("#mobile_hotspot").hide();
                    $("#direct_dotjobsMetaBoxSearch .hotspotparent_0").fadeIn();                    
                }else{
                    // turn on the already built mobile ad
                    $("#mobile_hotspot").show();                    
                }
            });
        });
    }    
    return flag;
}
function BuildBillboard(list){
    /**
    Builds the container divs for the billboard homepage scroll.
    Input
        :list: array object containing values converted from
                         the billboard object in the django template
    Returns:
        div_str: an HTML string containing all the divs
    **/    
    div_str="";
    for(i=0;i<list.length;i++){
        div_str += "<div "; 
            div_str += "class='direct_dotjobsBillboardImageBackground' ";
            div_str += "id='direct_billboardImage_"+i+"' ";
            div_str += "style='background-image: url( "+list[i].image_url+" );";
            div_str += "display: none;' ";
            div_str += "data-imagesource='"+list[i].image_url+"' ";
            div_str += "data-logo='"+list[i].logo_url+"' ";
            div_str += "data-sponsor='"+list[i].sponsor_url+"'>";
             
            div_str += "<em id='billboardImage_copyright_"+(i+1)+"' ";
                div_str += "data-copyright='"+list[i].copyright_info+"' ";
                div_str += "data-source='"+list[i].source_url+"' ";           
                div_str += "data-node='copyright' class='copyrightControl'>";
                div_str += "&copy;";
            div_str += "</em>";                        
        div_str += "</div>";
        //build hotspots if they exist
        if(typeof(list[i].hotspots[0])!='undefined'){                
                for(ii=0;ii<list[i].hotspots.length;ii++){
                    div_str += buildHotSpotHTML(
                        list[i].hotspots[ii],i,ii,false
                        );
                }
            }
    }
    return div_str;    
}
function buildHotSpotHTML(ad,i,ii,mobile_ad){
    /*** (8/31/12 Jason Sole)
    This function assembles the html for a single hotspot ad. It handles both
    the standard interactive version and the non-interactive mobile version.
    
    Inputs:
        :ad:        object; the hotspot ad object with all its properties
        :i:         int; the billboard loopcount
        :ii:        int; the hotspot loopcount with the cirrent billboard loop
        :mobile_ad: boolean; true if ad is being created for the mobile view 
        
    Returns:
        string of html text
    
    **/
    // set transparency level for background color
    alpha = ".85"
    // pull variables out of the object and assign defaults if they are missing 
    p_hex = var_value_or_default(ad.primary_color,"#FFFFFF");
    f_hex = var_value_or_default(ad.font_color,"#000000");
    b_hex = var_value_or_default(ad.border_color,"#000000");
    x =     var_value_or_default(ad.x,0);
    y =     var_value_or_default(ad.y,0);
    hs_title = var_value_or_default(ad.title,"");
    text =  var_value_or_default(ad.text,"");
    url =   var_value_or_default(ad.url,"");
    display_url = var_value_or_default(ad.display_url, "")
    
    // convert variables as needed
    p_r = hexToR(p_hex); //get RGB of red hex value
    p_g = hexToG(p_hex); //get RGB of green hex value
    p_b = hexToB(p_hex); //get RGB of blue hex value
    p_rgba = "rgba("+p_r+","+p_g+","+p_b+","+alpha+")"; //build rgba css value    
    x_coord = x-50;// wrapper has a left padding of 50px    
    
    if (display_url != "None") {
        clean_url = display_url;
    } else {
        // create the display url by slicing off the protocol and query string
        clean_url = url;
        if(clean_url.indexOf("//") != -1) {
            clean_url = ad.url.split("//")[1]; // Get rid of the protocol
        }
        clean_url = clean_url.split("?")[0]; // Get rid of everything after '?'
           // get rid of the trailing slash
        clean_url = clean_url.slice(-1) != "/" ? clean_url : clean_url.slice(0, -1);
    }

    // build the hotspot HTML
    div_str  = "";
    div_str += "<span class='hotspotWrapper hotspotparent_"+i+"'";
    div_str += "data-url='"+url+"' ";
    div_str += "data-name='"+hs_title+"'";
        
    if(mobile_ad){ // mobile ad has a unique id syntax
        div_str += "id='hotspot_mobile' ";
    }else{
        div_str += "id='hotspot_"+i+"_"+ii+"' ";
    }    
    div_str += "style='";
    if(!mobile_ad){ 
        div_str += "position: absolute; ";
        div_str += "display: none; ";
        div_str += "margin-top: "+y+"px; ";
        div_str += "margin-left: "+x_coord+"px; ";
    }
    div_str += "'>";                    
    div_str += "<a class='hotspotButton' data-url='"+url+"' data-name='"+hs_title+"'";
    if(!mobile_ad){
        div_str += "style='background: "+p_rgba+"; padding: 2px;' ";
    }
    div_str += "name='"+hs_title+"'><span style='border-color: #"+b_hex+";'></span></a>";
    div_str += "<span style='";
    if(!mobile_ad){
        div_str += "background: "+p_rgba+";";
        if(x>=500){
            div_str += " margin-left: -365px !important; ";
        }
    }
    div_str += "' class='hotspotDetail' ";
    if(url.indexOf("http://")>-1){
        div_str += "data-url='"+url+"' ";    
    }
    div_str += ">";
    div_str += "<p style='";
    if(!mobile_ad){
            div_str+= "border-color: #"+b_hex+"; color: #"+f_hex+"";
    }
    div_str += "'>";
    if(hs_title != ""){
        div_str += "<b>"+hs_title+"</b>";
    }
    div_str += text;
    div_str += "<a href='"+url+"' data-url='"+url+"' data-name='"+hs_title+"' target='_blank'>"+clean_url+"</a>";
    div_str += "</p>";
    div_str += "</span></span>";
    return div_str; // return the compiled html to the calling function.
}
// RGB conversion F(n)s from http://www.javascripter.net/faq/hextorgb.htm
function hexToR(h) {return parseInt((cutHex(h)).substring(0,2),16)}
function hexToG(h) {return parseInt((cutHex(h)).substring(2,4),16)}
function hexToB(h) {return parseInt((cutHex(h)).substring(4,6),16)}
function cutHex(h) {return (h.charAt(0)=="#") ? h.substring(1,7):h}

function BuildHotSpotFunction(){
    /**
    Function that builds out the click function for billboard hotspots. It is
    run whenever the Billboards are written. This is not at document.ready due 
    to the mobile detection required prior to building the billboards.
    
    Inputs:    
        None
 
    **/
    $("#direct_dotjobsMetaBoxSearch .hotspotButton").mouseenter(function(){
        target = $(this);
        $("#direct_dotjobsMetaBoxSearch .hotspotWrapper").each(function(){
            if($(this).attr('id') != target.parent().attr('id')){
                $(this).removeClass('activeHotspot');
            }
        });
        target.parent().toggleClass('activeHotspot');
        target.parent().children(".hotspotDetail").fadeIn(200);
    });
    $(".hotspotDetail").click(function(){
        targetURL = $(this).attr('data-url');
        if(typeof(targetURL)!='undefined'){
            window.open(targetURL);
        }
    });
    $(".hotspotWrapper").mouseleave(function(){
        $(".activeHotspot .hotspotDetail").fadeOut(200);
        $("#direct_dotjobsMetaBoxSearch .hotspotWrapper").each(function(){
            $(this).removeClass('activeHotspot');
        });
    });
}
function BuildSponsorLogo(logo_url, sponsor_url){
    /**
    Builds the initial sponsorship logo for a billboard site.
    Input
        :logo_url: the source url for the sponsorship image logo
        :sponsor_url: the site url that the logo links to
    Returns:
        :logo: the html img tag to display the logo
    **/
    link_text = "Sponsor<span>"+window.location.hostname+"</span>";    
    sponsor_link = "http://universe.jobs/employment-marketing/";
    sponsor_link+= "?utm_source=network-microsites&utm_medium=banner";
    sponsor_link+= "&utm_campaign=billboard-sponsorship";
    if(logo_url=="" || logo_url.toLowerCase()=="none"){
        logo = '<a id="sponsor-dotjobs" target="_blank" ';
        logo+= 'href="'+sponsor_link+'">'+link_text+'</a>';
    }else{
        logo='<a href="';
        if(sponsor_url=="None"){
            logo+='">';
        }else{
            logo+=sponsor_url+'">';
        }
        logo+='<img src="'+logo_url+'"></a>';
    }
    return logo;
}

function rotateBillboardImage(id){
    /**
    This function switches the background of the billbaord section in the
    the home_page_billboard template.
    
    :id: The id value (int) of the billboard image to switch to.
    
    This function also swaps the active number time and sponsor logo in the
    billboard navigation bar.
    **/
    currentBrandImage = billboardImagePosition;
    if(id=="next"){
        billboardImagePosition++;
        id=billboardImagePosition;
    }else if(id=="prev"){    
        billboardImagePosition--;
        id=billboardImagePosition;
    }else{
        billboardImagePosition=id;
    }        
    if(billboardImagePosition>billboardImagePositionMax){
        billboardImagePosition=0;
        id=0;
    }else if(billboardImagePosition<0){
        billboardImagePosition=billboardImagePositionMax;
        id=billboardImagePositionMax;
    }
    newDiv = $("#direct_billboardImage_"+id);
    /*Transition from one image to another*/
    $("#direct_dotJobsImageControls span").removeClass("active");
    $("#direct_dotjobsMetaBoxSearch .hotspotWrapper").hide();
    $(".direct_dotjobsBillboardImageBackground").hide();
    /*Handle the sponsor logo*/
    var logoImg = $("#direct_dotjobsBottomSponsor img");
    var sponsorURL = $("#direct_dotjobsBottomSponsor a");
    logoImg.hide();
    var newLogo = newDiv.attr("data-logo");
    var newSponsor = newDiv.attr("data-sponsor");
    var placeHolder = "//d2e48ltfsb5exy.cloudfront.net/100x50/logo.gif";
    if(newLogo=="" || newLogo.toLowerCase()=="none"){
        newLogo=placeHolder;
    }
    logoImg.attr("src",newLogo);
    if(newSponsor!='None'){
    sponsorURL.attr("href",newSponsor);
    }
    /*Show the new billboard*/
    logoImg.fadeIn();
    newDiv.fadeIn();
    $(".hotspotparent_"+id).fadeIn();
    $("#direct_imageControl_"+id).addClass("active");        
}
function fisherYates ( myArray ) {
    /**
    Array randomizing function.
    Inputs
        :myArray: array to randomly reorder    
    Returns
        :myAray: randomized Array
    Credit:
        http://sedition.com/perl/javascript-fy.html
    **/
    var i = myArray.length;
    if ( i == 0 ) return false;
    while ( --i ) {
        var j = Math.floor( Math.random() * ( i + 1 ) );
        var tempi = myArray[i];
        var tempj = myArray[j];
        myArray[i] = tempj;
        myArray[j] = tempi;
    }
    return myArray;
}
function detectWidth(){
    /**
    Utility Function to return screen width. This is used when css media
    width detection will not get the job job.
    Inputs
        None
    Returns
        :width: the width of the browser window
    **/
    width=false;
    if (document.body && document.body.offsetWidth) {
        width = document.body.offsetWidth;        
    }else if (document.compatMode=='CSS1Compat' &&
        document.documentElement &&
        document.documentElement.offsetWidth ) 
        {
        width = document.documentElement.offsetWidth;
    }else{
        width = window.innerWidth;
    }
    return width;    
}
function populateCarousel(){
    /* Randomize the array. */

    if (featured_exists==false) {
        companyLogos = fisherYates(companyLogos);
    }

    /**
    Builds HTML for the company logo carousel.
    Globals
        :companyLogos: array object containing values converted from
                       the django template.
    Returns:
        :newImages: an HTML string containing the first seven images.
    **/
    var newImages = "";
    var newImage = "";
    
    if (companyLogos.length < 7) {
        var length = companyLogos.length;
    } else {
        length = 7;
    }
    
    for(i=0;i<length;i++){
        newImage ='<a href="'+companyLogos[i].url+'"';
        newImage+=' class="icon"><img src="//d2e48ltfsb5exy.cloudfront.net/100x50/logo.gif"';
        newImage+=' style="background-image: url('+companyLogos[i].image+')"';
        newImage+=' alt="'+companyLogos[i].name+' Careers"/></a>';
        newImages+=newImage
    }
    return newImages;
}
function var_value_or_default(node,def){
    /**
    Sub method to check for undefined values.
    inputs:
        :node:  the object node to test
        :def:   the default value for the node
    returns:
        :value: value of node or value of def
        
    **/    
    value = (typeof(node)!='undefined') ? node : def;
    return value;
}


function get_toolbar(site_name) {
    var site = encodeURIComponent(window.location.protocol + '//' + window.location.hostname),
        url = ABSOLUTE_URL + "topbar/?site_name=" + site_name + "&site=" + site + "&impersonating=" + impersonating;
    $.ajax({
        //url: "https://secure.my.jobs/topbar/?site_name=" + site_name + '&site=' + site,
      url: url,
        dataType: "jsonp",
        type: "GET",
        jsonpCallback: 'populate_toolbar',
        crossDomain: true,
        processData: false,
        headers: {'Content-Type': 'application/json', Accept: 'text/javascript'}
    });
}

function populate_toolbar(data) {
    $(".direct_dotjobsWideHeader").prepend(data);
}
