


$(document).ready(function(){
	var number= '12';
	
	$.get('/init/'+number, function(photos){
		var lats=[]
		var lons =[]
		for (i=0; i<photos.points.length; i++){
			var pic = photos.points[i];
			var url = pic.url;
			lats[i]=pic.lat
			lons[i]=pic.lon
			var  htmlpic = $("#port")
			.append("<div class='col-sm-6 col-md-3 isotope-item web-design'>\
								<div class='image-box'>\
									<div id='pic"+String(i)+"' class='overlay-container' >\
										<img lat='"+ String(pic.lat)+"' lon='"+ String(pic.lon)+"' src='"+url+"' alt='"+pic.scene1+"' style='width:300px; height: 200px; '>\
										<a class='overlay' data-toggle='modal' data-target='#project-1'>\
											<!--<i class='fa fa-search-plus'></i>-->\
											<span>"+pic.scene1+"</span>\
										</a>\
									</div>\
									<!--<a class='btn btn-default btn-block' data-toggle='modal' data-target='#project-1' >"+pic.scene1+"</a>-->\
								</div></div>");
			$("#pic"+String(i)).on("click", function(){
				
				$("#srch-term").val($(this).children("img").attr("alt"));
				$("#srch-term").submit();
				$("html, body").animate({ scrollTop: $("#map").offset().top-120 }, "slow");
				var coords = new L.LatLng(parseFloat($(this).children("img").attr("lat")), parseFloat($(this).children("img").attr("lon")));
				map.panTo(coords);
				map.setZoom(15);
				


			});
			


			//.append("<a href='"+url+"' id='pic"+String(i)+"'>")
			//var name = "#pic"+String(i);

			

		};


		
		
	});

/*	$("#latest").justifiedGallery({
    rowHeight : 200,
    lastRow : 'nojustify',
    margins : 5
});*/

});


