var base_tile = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 18,
          minZoom: 1,
          attribution: 'Map data (c) <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
      });

      $(".tt-hint").addClass("form-control");


      

      /*
      Bounding box.
      */
      var southWest = L.latLng(-90, -180),
          northEast = L.latLng(90, 180),
          bounds = L.latLngBounds(southWest, northEast);

      /*
      Creates the map and adds the selected layers
      */
      



  

      var map = L.map('map', {
                                       center:[37.863372, -122.156245],
                                       zoom: 7,
                                       maxBounds: bounds,
                                       layers: [base_tile]
                                     });

      var heat = L.heatLayer([], {maxZoom: 7, radius: 30, blur: 40});
      heat.addTo(map);

      var baseLayer = {
        "Base Layer": base_tile
      };


      var layer_list = { "heatmap" : heat
      
      };

      var control = L.control.layers(baseLayer, layer_list);
      control.addTo(map);
      //L.control.layers(heatmapLayer, layer_list).addTo(map);

      //cluster group
      //var clusteredmarkers = L.markerClusterGroup();
      //section for adding clustered markers
      
      //add the clustered markers to the group anyway

      //map.addLayer(clusteredmarkers);
      /*
      var marker_1_icon = L.AwesomeMarkers.icon({ icon: 'info-sign',markerColor: 'blue',prefix: 'glyphicon',extraClasses: 'fa-rotate-0'});
      var marker_1 = L.marker([32.796149, 
              -117.25974],
              {'icon':marker_1_icon}
              );
      marker_1.bindPopup("<a><img src=http://farm4.staticflickr.com/3096/2848868873_0187db5fd6.jpg></img><BR>ocean</a>");
      marker_1._popup.options.maxWidth = 300;
      map.addLayer(marker_1)
      */
      
   

      var plotlayers=[];
      var markers = new L.markerClusterGroup({maxClusterRadius: 60}); //L.FeatureGroup();


      

   		$("#srch-term").submit(function(event){
        event.preventDefault();
        var query = $("#srch-term").val();
   			$.get('/category/'+ query, function(jd) {

          
          markers.clearLayers();
          heat.setLatLngs([]);

          //var arr = $.map(jd, function(el) { return el; });
          /*var heat = L.heatLayer(arr,{
            radius: 20,
            blur: 15, 
            maxZoom: 17,
        }).addTo(map);
*/
          var j=0;
          for (i=0; i<jd.points.length; i++){
            var point = jd.points[i];
            var divNode = document.createElement('DIV');
            divNode.className = "popup-div";
            divNode.innerHTML = "<a href="+point.url+ " target='_blank'><img class='lazyload' src='static/js/images/712.gif' data-src='"+ point.url+"' width=300 height=60%></img></a><BR>\
            <a href='https://www.google.com/maps/dir//"+point.lat+","+point.lon+"/' target='_blank' > Get Directions: \
            "+point.scene1+"</a><BR>"+point.sval1;
            
            var marker = L.marker([point.lat,point.lon])
            marker.bindPopup(divNode);
            markers.addLayer(marker);
            var latlng = L.latLng(point.lat,point.lon, 100*point.sval1);
            heat.addLatLng(latlng);
          };

          map.addLayer(markers);

            

        
          control.addOverlay(markers, query );   




        });
   		
   		});

$("#srch-term").on('keydown', function(event){
    e = jQuery.Event("keydown");
    e.keyCode = e.which = 40;

    if (event.which == 13){
        event.stopPropagation();
        $("#srch-term").trigger(e);
        e.keyCode = e.which = 9 ;            
        $("#srch-term").trigger(e);
        $("#srch-term").submit();
        return false;
      }

});