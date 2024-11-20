function drawANPBorder(anpId, baseUrlApi, bearerToken, map, drawControl){
  $.ajax({
    method: "GET",
    url: baseUrlApi + "/getANP/" + anpId,
    headers: {
      'Authorization': 'Bearer ' + bearerToken,
      'Content-Type': 'application/json'
    }
  }).done(function(data) {
    console.log(data);
    var border = data.border;
    var centroid = data.centroid;

    var anp = L.geoJSON(border, {
        style: function (feature) {
            return {
              color: 'white', 
              fillOpacity: 0.0
            };
        }
    });
    anp.addTo(map);
    map.fitBounds(anp.getBounds());
    $('#getGrid').prop("disabled", false);
    map.removeControl(drawControl);
  });
}

function drawANPGrid(anpId, baseUrlApi, bearerToken, map, currentZoom, currentColor, drawControl, idColours, colours, color1, color2, color3, color4, color5, colouration){
  
  $('#cat1').on('click', function(){
    currentColor = color1;
  });
  $('#cat2').on('click', function(){
      currentColor = color2;
  });
  $('#cat3').on('click', function(){
      currentColor = color3;
  });
  $('#cat4').on('click', function(){
      currentColor = color4;
  });
  $('#cat5').on('click', function(){
      currentColor = color5;
  });

  $("#sendColouration").off("click");
  $('#sendColouration').on('click', function(){
    $.ajax({
      method: "POST",
      url: baseUrlApi + "/createColouration/" + anpId,
      contentType: 'application/json',
      headers: {
        'Authorization': 'Bearer ' + bearerToken,
        'Content-Type': 'application/json'
      },
      data: JSON.stringify({colouration: Object.values(colouration)})
    }).done(function(data){
      if(data.success){
        alert('Datos envíados correctamente');
        //location.reload()
      } else {
        alert('Ocurrió un error, intente nuevamente');
      }
    });
  });
  
  $.ajax({
    method: "GET",
    url: baseUrlApi + "/getGridANP/" + anpId,
    headers: {
      'Authorization': 'Bearer ' + bearerToken,
      'Content-Type': 'application/json'
    }
  }).done(function(data) {
    colouration = []
    data.grid.forEach((item) => {
      var cell = L.geoJSON(item.border, {
        style: function (feature) {
          if(item.id_colour !== null && item.id_colour!== undefined){
            return {
              color: idColours[item.id_colour],
              fillOpacity: 0.3
            };
          } else {
            return {
              color: 'darkgray', 
              fillOpacity: 0.0
            };
          }
        }
      });
      cell.addTo(map);
      cell.on('click', function (e) {
        var layer = e.target;
        currentZoom = map.getZoom();
        //console.log('currentZoom = ', currentZoom);
        if(14 <= currentZoom && currentZoom <= 16){
          $('#sendColouration').show();
          if(currentColor===color5){
            layer.setStyle({
                color: currentColor,
                fillOpacity: 0.0
            });
            console.log(item.id);
            delete colouration[item.id];
          } else {
            layer.setStyle({
                color: currentColor,
                fillOpacity: 0.3
            });
          }
          colouration[item.id] = {id: item.id, colour: colours[currentColor]};
        } else if(currentZoom < 14) {
          alert('Nivel de zoom no permitido para colorear, acerque más');
        } else {
          alert('Nivel de zoom no permitido para colorear, aleje más');
        }
        
      });
    });

    map.addControl(drawControl);
    var editableLayers = new L.FeatureGroup();
    map.addLayer(editableLayers);
    map.on('draw:created', function(e) {
      var type = e.layerType,
      layer = e.layer;
      map.removeControl(drawControl);
      var geojson = layer.toGeoJSON();
      var geojsonString = geojson;
      
      $.ajax({
        method: "POST",
        url: baseUrlApi + "/get_cells",
        headers: {
          'Authorization': 'Bearer ' + bearerToken,
          'Content-Type': 'application/json'
        },
        data: JSON.stringify({polygon: geojsonString, id_anp: anpId})
      }).done(function(data) {
        console.log(data);
        $('#showGrid').show();
        map.eachLayer(function (layer) {
          if (layer instanceof L.Polygon) {
              map.removeLayer(layer);
          }
        });
        colouration = []
        data.cells.forEach((item) => {
          var cell = L.geoJSON(item.border, {
            style: function (feature) {
              if(item.id_colour !== null && item.id_colour!== undefined){
                return {
                  color: idColours[item.id_colour],
                  fillOpacity: 0.3
                };
              } else {
                return {
                  color: 'darkgray', 
                  fillOpacity: 0.0
                };
              }
            }
          });
          cell.addTo(map);
          cell.on('click', function (e) {
            var layer = e.target;
            currentZoom = map.getZoom();
            //console.log('currentZoom = ', currentZoom);
            if(14 <= currentZoom && currentZoom <= 16){
              $('#sendColouration').show();
              if(currentColor===color5){
                layer.setStyle({
                    color: currentColor,
                    fillOpacity: 0.0
                });
                console.log(item.id);
                delete colouration[item.id];
              } else {
                layer.setStyle({
                    color: currentColor,
                    fillOpacity: 0.3
                });
              }
              colouration[item.id] = {id: item.id, colour: colours[currentColor]};
            } else if(currentZoom < 14) {
              alert('Nivel de zoom no permitido para colorear, acerque más');
            } else {
              alert('Nivel de zoom no permitido para colorear, aleje más');
            }
            
          });
        });
        
      });

      $('#getGrid').prop("disabled", true);
    });

  });
}

$(document).ready(function(){

    var inSession = $.cookie('logged');
    if(inSession === null || inSession === undefined || inSession === false){
      window.location.replace("/login.html");
    }
    var idUser = $.cookie('id_user');
    var bearerToken = $.cookie('bearer_token');
    console.log(bearerToken);

    var map = L.map('map').setView([24.186550, -101.617894], 5);
    var baseLayers = {
      "GoogleMaps": L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',{
              maxZoom: 20,
              subdomains:['mt0','mt1','mt2','mt3']
      }),
      "OpenStreetMap": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
              attribution: '&copy; OpenStreetMap contributors'
      }),        
    };
    baseLayers.GoogleMaps.addTo(map);
    L.control.layers(baseLayers).addTo(map);

    var baseUrlApi = 'http://127.0.0.1:555';
    //var baseUrlApi = 'http://api:5000';
    var baseUrlApi = 'https://cosmos-validacion-integridad-sipecam.conabio.gob.mx/api/';
    var anpId = null;
    var colouration = [];
    const colours = {
      '#0571b0': 1,
      '#92c5d3': 2,
      '#f4a582': 3,
      '#ca0020': 4,
      'darkgray': 0
    };
    const idColours = {
      1: '#0571b0',
      2: '#92c5d3',
      3: '#f4a582',
      4: '#ca0020'
    };
    const color1 = '#0571b0';
    const color2 = '#92c5d3';
    const color3 = '#f4a582';
    const color4 = '#ca0020';
    const color5 = 'darkgray';
    var currentColor= color1;
    var currentZoom = 0;

    var CustomControl = L.Control.extend({
      onAdd: function(map) {
            var button = L.DomUtil.create('button');
            button.id = 'sendColouration';
            button.innerHTML = 'Enviar coloración';
            button.title = 'Enviar coloración';
            button.class = 'btn btn-primary'
            L.DomUtil.addClass(button, 'btn btn-primary');
            return button;
      },
      onRemove: function(map) {
      }
    }); 

    var CustomControlShowGrid = L.Control.extend({
      onAdd: function(map) {
          var button = L.DomUtil.create('button');
          button.id = 'showGrid';
          button.innerHTML = 'Mostrar malla completa';
          button.title = 'Mostrar malla completa';
          button.class = 'btn btn-primary'
          L.DomUtil.addClass(button, 'btn btn-primary');
          return button;
      },
      onRemove: function(map) {
      }
    }); 

    new CustomControl({ position: 'topright' }).addTo(map);
    new CustomControlShowGrid({ position: 'bottomright' }).addTo(map);

    $('#sendColouration').hide();
    $('#showGrid').hide();

    var editableLayers = new L.FeatureGroup();
    map.addLayer(editableLayers);
    var options = {
      position: 'topleft',
      draw: {
        polygon: {
          allowIntersection: false, 
          drawError: {
            color: '#e1e100', 
            message: '<strong>Oh snap!<strong> you can\'t draw that!'
          },
          shapeOptions: {
            color: '#97009c'
          }
        },
        polyline: {
          shapeOptions: {
            color: '#f357a1',
            weight: 10
              }
        },
        polyline: false,
        circle: false,
        polygon: true,
        marker: false,
        rectangle: false,
      },
      edit: {
        featureGroup: editableLayers, 
        remove: true
      }
    };

    var drawControl = new L.Control.Draw(options);

    $.ajax({
        method: "GET",
        url: baseUrlApi + "/getANPs",
        headers: {
          'Authorization': 'Bearer ' + bearerToken,
          'Content-Type': 'application/json'
        }
    }).done(function(data){
      //console.log(data)
      $('#anpSelector').empty();
      $('#anpSelector').append('<option value="0">--</option>');
      data.anps.forEach((item) => {
        $('#anpSelector').append('<option value="' + item.id + '">' + item.nombre+ '</option>')
      });
    });

    $('#anpSelector').on('change', function(){
      map.eachLayer(function (layer) {
        if (layer instanceof L.Polygon) {
            map.removeLayer(layer);
        }
      });
      
      $('#sendColouration').hide();
      console.log('Loading new ANP');
      anpId =  $('#anpSelector').val();
      drawANPBorder(anpId, baseUrlApi, bearerToken, map, drawControl);
    });

  $('#getGrid').on('click', function(){
    drawANPGrid(anpId, baseUrlApi, bearerToken, map, currentZoom, currentColor, drawControl, idColours, colours, color1, color2, color3, color4, color5, colouration);
  });

  $('#showGrid').on('click', function(){
    drawANPBorder(anpId, baseUrlApi, bearerToken, map, drawControl);
    drawANPGrid(anpId, baseUrlApi, bearerToken, map, currentZoom, currentColor, drawControl, idColours, colours, color1, color2, color3, color4, color5, colouration);    
    $(this).hide();
  });

  $('#logout').on('click', function(){
    document.cookie = 'logged=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    window.location.replace("/login.html");
  });

});