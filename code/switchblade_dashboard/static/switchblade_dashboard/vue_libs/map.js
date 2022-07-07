const CancelToken = axios.CancelToken;

map_control = new Vue({
    el: '#map_container',
    delimiters: ['[[', ']]'],
    data: {
        // Map
        map: null,

        // Theme
        themes: null,
        currentTheme: "",
        markersLayer: null,
        markers: {},
        markersData: {},
        useCluster: false,
        legend: null,
        clusterLegend: {},
        usePolygons: false,
        useSVGMarkers: false,
        filterForm: null,
        filterFields: [],
        mapFilters: {},

        // Miscellaneous
        is_loading: false,
        in_configuration: true,
        is_processing: false,
        axios_source: null,
        siteIds: null,

        // Zoom markers problem
        // zoom_too_high: false,
        // min_zoom_to_load_sites: 10

    },
    watch: {
        currentTheme: function(val, oldVal) {
            this.getConfigurations();
        }
    },
    mounted() {
        this.initMap();
        this.setEvents();
        this.addControls();
        this.getThemes();
    },
    updated: function () {
        $('.select2').select2({
            allowClear: true
        });

        $('.date-range').daterangepicker({
            opens: 'left',
            autoUpdateInput: false,
              locale: {
                  cancelLabel: 'Clear',
                  format: 'YYYY-MM-DD'
              }
        });

        $('.date-range').on('apply.daterangepicker', function(ev, picker) {
            if (picker.startDate.format('YYYY-MM-DD') === picker.endDate.format('YYYY-MM-DD')) {

                $(this).val(picker.startDate.format('YYYY-MM-DD'));

            } else {
                $(this).val(picker.startDate.format('YYYY-MM-DD') + ' until ' + picker.endDate.format('YYYY-MM-DD'));
            }
        });

        $('.date-range').on('cancel.daterangepicker', function(ev, picker) {
          $(this).val('');
        });

        $('.date-time-range').daterangepicker({
            opens: 'left',
            timePicker: true,
            autoUpdateInput: false,
            timePicker24Hour: true,
              locale: {
                  cancelLabel: 'Clear',

              }
        });

        $('.date-time-range').on('apply.daterangepicker', function(ev, picker) {
          $(this).val(picker.startDate.format('YYYY-MM-DD HH:mm') + ' until ' + picker.endDate.format('YYYY-MM-DD HH:mm'));
        });

        $('.date-time-range').on('cancel.daterangepicker', function(ev, picker) {
          $(this).val('');
        });

    },
    methods: {
        initMap: function() {

            //Map Options
            var mapOptions = {
                zoomControl: false,
                attributionControl: false,
                center: [-20.184279, -48.690645],
                zoom: 8,
                layers: [
                    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                        minZoom: 6,
                        maxZoom: 17,
                        id: "osm.streets"
                    })
                ]
            };

            //Render Main Map
            this.map = L.map("map", mapOptions);
        },

        setEvents: function() {

            let self = this;

            // Edit Button click
            $('#toggledraw').click(function(e) {
                $(".leaflet-draw").fadeToggle("fast", "linear");
                $(".leaflet-draw-toolbar").fadeToggle("fast", "linear");
                this.blur();
                return false;
            });

            // Show sidebar
            $('#sidebar').show();

            // Map move
            this.map.on('moveend', function() { if (!self.in_configuration) {

                self.cancelAndRedoMarkers();

            } });

            // // Map Zoom
            // this.map.on('zoomstart', function() {
            //     let zoom_level = self.map.getZoom();
            //     if(zoom_level < self.min_zoom_to_load_sites)
            //         self.zoom_too_high = true;
            //     else {
            //         self.zoom_too_high = false;
            //     }
            // });

        },

        cancelAndRedoMarkers: function() {
            var self = this;

            if (this.axios_source != null) {
                this.axios_source.cancel('Operation canceled by the user.');
            }


            this.is_processing = false;
            this.getMarkers();
        },

        addControls: function() {
            let self = this;

            //Render Zoom Control
            L.control.zoom({ position: "topleft" }).addTo(this.map);

            // Search
           this.map.addControl(new L.Control.Search({
                position: "topright",
                collapsed: false,
                hideMarkerOnCollapse: true,
                textPlaceholder: 'Search...',
                sourceData: self.searchPoint,
                zoom: 13,
                initial: false,
                marker: {
                    icon: null,
                    circle: {radius: 20, color: '#DD4B39', opacity: 1}
                }
           }).on('search:locationfound', function () {
                var search = this;

                // console.log('aqui');
                // console.log(this);

                setTimeout(function(){search._map.removeLayer(search._markerSearch);}, 3000);
           }));

            // Initialize Sidebar
            var sidebar = L.control.sidebar({autopan: false, container: "sidebar", position: "right"}).addTo(this.map);

            /* ----- Leaflet Draw ----- */

            var editableLayers = new L.FeatureGroup();
            this.map.addLayer(editableLayers);

            var drawOptions = {
                position: "topleft",
                draw: {
                    polyline: true,
                    polygon: {
                        allowIntersection: false, // Restricts shapes to simple polygons
                        drawError: {
                            color: "#e1e100", // Color the shape will turn when intersects
                            message: "<strong>Warning:</strong> You can't draw that!" // Message that will show when intersect
                        }
                    },
                    circle: true, // Turns off this drawing tool
                    rectangle: true,
                    marker: true
                },
                edit: {
                    featureGroup: editableLayers, //REQUIRED!!
                    remove: true
                }
            };

            var drawControl = new L.Control.Draw(drawOptions);
            this.map.addControl(drawControl);

            this.map.on(L.Draw.Event.CREATED, function(e) {
                var type = e.layerType,
                layer = e.layer;

                if (type === "marker")
                    layer.bindPopup("Lat: " + layer.getLatLng().lat + ", Long: "  + layer.getLatLng().lng).openPopup();

                editableLayers.addLayer(layer);

                $(".drawercontainer .drawercontent").html(JSON.stringify(editableLayers.toGeoJSON()));
            });

            this.map.on(L.Draw.Event.EDITSTOP, function(e) {
                $(".drawercontainer .drawercontent").html(
                    JSON.stringify(editableLayers.toGeoJSON())
                );
            });

            this.map.on(L.Draw.Event.DELETED, function(e) {
                $(".drawercontainer .drawercontent").html("");
            });
        },

        getThemes: function() {
            axios.get('themes/',
            {
                headers: {'X-CSRFToken': csrf_token}
            }).then(response => {
                if(!$.isEmptyObject(response.data.themes)) {
                    this.themes = response.data.themes;
                    this.currentTheme = (!$.isEmptyObject(response.data.default_theme)) ? response.data.default_theme : Object.keys(this.themes)[0];
                } else {
                    this.currentTheme = null;
                }
            }).catch((error) => {
                $.notify(error.response.data, {type: 'error'});
            });
        },

        getConfigurations: function() {
            this.in_configuration = true;

            var url = (this.currentTheme != "" && this.currentTheme != null) ? 'config/?theme=' + this.currentTheme : 'config/';

            axios.get(url,
            {
                headers: {'X-CSRFToken': csrf_token}
            }).then(response => {
                this.usePolygons = response.data.use_polygons;
                this.useSVGMarkers = response.data.use_svg_marker;
                this.clusterLegend = response.data.cluster_legend;
                this.setFilterForm(response.data.filter);
                this.mapFilters = {};
                this.addLegend(response.data.legend);
                this.clearMap();
                this.setMarkersLayer(response.data.use_marker_cluster);
                this.in_configuration = false;
                this.cancelAndRedoMarkers();
                var self = this;


            }).catch((error) => {

                console.log(error);
                if(error.response !== undefined) {
                    $.notify(error.response.data, {type: 'error'});
                }
                this.in_configuration = false;
            });
        },

        addLegend: function(legendData) {

            if (!legendData || Object.keys(legendData).length == 0) {
                return;
            }

            if (this.legend)
                this.map.removeControl(this.legend);

            this.legend = L.control({position: 'bottomleft'});

            this.legend.onAdd = function (map) {

                var div = L.DomUtil.create('div', 'info-legend legend');

                $.each(legendData, function(grade, color) {
                    div.innerHTML += '<p><i style="background:' + color + '"></i> ' + grade + '</p>';
                });

                return div;
            };

            this.legend.addTo(this.map);
        },

        setFilterForm: function(filter) {

            if(!filter) {
                return;
            }

            this.filterForm = filter['form'];
            this.filterFields = filter['form_fields'];

        },

        setMapFilters: function() {

            var form = $('#formMapFilter')[0];

            // var elements = getAllFormElements(form);

            var map_filter = this.filterFields.reduce(function(map, el) {
                map[el] = $('#id_'+el)[0].value;
                return map;
            }, {});

            this.mapFilters = map_filter;

            $.notify('Filter applied.', {type: 'info'});

            this.cancelAndRedoMarkers();
        },

        setMarkersLayer: function(useCluster) {
            this.useCluster = useCluster;

            if (useCluster){
                if (!$.isEmptyObject(this.clusterLegend))
                    this.markersLayer = this.getCustomClusters();
                else
                    this.markersLayer = L.markerClusterGroup();

                this.map.addLayer(this.markersLayer);
            } else {
                this.markersLayer = L.geoJSON();
                this.markersLayer.addTo(this.map);
            }
        },

        getCustomClusters: function() {
            let self = this;

            return L.markerClusterGroup({
                removeOutsideVisibleBounds: true,
                iconCreateFunction: function (cluster) {
                    var childCount = cluster.getChildCount();
                    var markers = cluster.getAllChildMarkers();
                    var maxLevel = Math.max.apply(Math, markers.map(function(marker) {
                        return marker.feature.properties.cluster_level;
                    }));

                    if (maxLevel in self.clusterLegend) {
                        return new L.DivIcon({
                            html: '<div style="background-color: ' + self.clusterLegend[maxLevel] + ';"><span>' + childCount + '</span></div>',
                            className: 'marker-cluster marker-cluster-large',
                            iconSize: new L.Point(40, 40)
                        });
                    } else {
                        return new L.DivIcon({
                            html: '<div style="background-color: #FFFFFF;"><span>' + childCount + '</span></div>',
                            className: 'marker-cluster marker-cluster-large',
                            iconSize: new L.Point(40, 40)
                        });
                    }
                }
            });
        },

        getMarkers: function() {

            // if (!this.in_configuration && !this.zoom_too_high) {
            if (!this.in_configuration && !this.is_processing) {

                this.is_processing = true;
                this.$forceUpdate();

                var bounds = {
                    'minX': this.map.getBounds().getWest(),
                    'minY': this.map.getBounds().getSouth(),
                    'maxX': this.map.getBounds().getEast(),
                    'maxY': this.map.getBounds().getNorth()
                };

                let self = this;

                var source = CancelToken.source();
                this.axios_source = source;

                axios.post('points/', {'bounds': bounds, 'theme': this.currentTheme, 'filter': this.mapFilters},
                    {
                        headers: {'X-CSRFToken': csrf_token},
                        cancelToken: source.token
                    }).then(response => {

                    if ((self.usePolygons) && (self.useCluster)){
                        this.setPolygonMarkers(response.data.polygons, response.data.polygons_to_remove);
                        this.setClusterMarkers(response.data.points, response.data.points_to_remove);
                    } else if (self.usePolygons) {
                        this.setPolygonMarkers(response.data.polygons, response.data.polygons_to_remove);
                    } else if (self.useCluster) {
                        this.setClusterMarkers(response.data.points, response.data.points_to_remove);
                    } else {
                        this.setDefaultMarkers(response.data.points);
                    }

                    self.is_processing = false;

                    setTimeout(function () {
                        self.cancelAndRedoMarkers();
                    }, 60000);

                }).catch((error) => {
                    // console.log(error);
                    if(error.response !== undefined) {
                        $.notify(error.response.data, {type: 'error'});
                    }
                    if (!axios.isCancel(error)) {
                        self.is_processing = false;
                        // console.log('Request canceled', error.message);
                      }

                });
            }
        },

        setPolygonMarkers: function(polygons, received_polygons_to_remove_ids) {

            let self = this;

            var received_polygons_ids = polygons.map(p => p.properties.id);
            var current_polygons_ids = Object.keys(self.markers).map(k => parseInt(k)).filter(k => !received_polygons_to_remove_ids.includes(k));

            var registered_polygons_ids = received_polygons_ids.filter(k => current_polygons_ids.includes(k));
            var non_registered_polygons_ids = received_polygons_ids.filter(k => !current_polygons_ids.includes(k));
            var polygons_to_remove_ids = Object.keys(self.markers).map(k => parseInt(k)).filter(k => received_polygons_to_remove_ids.includes(k));

            var received_polygons_icon_colors = Object.keys(polygons).reduce(function(map, key) {
                map[polygons[key].properties.id] = polygons[key].properties.color;
                return map;
            }, {});

            var polygons_to_update_icon_ids = registered_polygons_ids.filter(id => self.markersData[id].icon_color !== received_polygons_icon_colors[id]);

            var polygons_to_proccess = polygons.filter(p => !received_polygons_to_remove_ids.includes(p.properties.id) && (non_registered_polygons_ids.includes(p.properties.id) || polygons_to_update_icon_ids.includes(p.properties.id)));

            polygons_to_update_icon_ids.forEach(function(i) {
                self.markersLayer.removeLayer(self.markers[i]);
            });

            polygons_to_remove_ids.forEach(function(i) {
                self.markersLayer.removeLayer(self.markers[i]);
                delete self.markers[i];
                delete self.markersData[i];
            });

//            L.geoJSON(polygons_to_proccess).addTo(self.map);


            $.each(polygons_to_proccess, function(index, polygon) {

                // polygon: { id: 1, name: 'XXX', color: 'xxx', points: []

                var geoJsonLayer = L.geoJSON(polygon, {

                    onEachFeature: function (feature, layer) {

                        self.markers[feature.properties.id] = polygon;
                        self.markersData[feature.properties.id] = {
                            'icon_color': feature.properties.color
                        };

                        layer.bindTooltip(feature.properties.name, {permanent: true, direction:"center", className: "polygon-name"});
                        layer.on('click', function (e) {
                            self.markerClick(feature.properties.id, feature.properties.center);
                        });
                        layer.setStyle({fillColor: feature.properties.inner_color, color: feature.properties.color});
                    }
                })
                if (polygon['properties']['id'] in self.markers)
                    self.markersLayer.removeLayer(self.markers[polygon['properties']['id'] ])

                self.markers[polygon['properties']['id']] = geoJsonLayer;
                geoJsonLayer.addTo(self.markersLayer);
            });
        },

        setClusterMarkers: function(points, received_points_to_remove_ids) {
            let self = this;

            var received_point_ids = points.map(p => p.properties.id);

            var current_point_ids = Object.keys(self.markers).map(k => parseInt(k)).filter(k => !received_points_to_remove_ids.includes(k));

            var registered_points_ids = received_point_ids.filter(k => current_point_ids.includes(k));
            var non_registered_points_ids = received_point_ids.filter(k => !current_point_ids.includes(k));
            var points_to_remove_ids = Object.keys(self.markers).map(k => parseInt(k)).filter(k => received_points_to_remove_ids.includes(k));

            var received_point_icon_colors = Object.keys(points).reduce(function(map, key) {
                map[points[key].properties.id] = points[key].properties.color;
                return map;
            }, {});

            var points_to_update_icon_ids = registered_points_ids.filter(id => self.markersData[id].icon_color !== received_point_icon_colors[id]);
            var points_to_proccess = points.filter(p => !received_points_to_remove_ids.includes(p.properties.id) && (non_registered_points_ids.includes(p.properties.id) || points_to_update_icon_ids.includes(p.properties.id)));

            points_to_update_icon_ids.forEach(function(i) {
                self.markersLayer.removeLayer(self.markers[i]);
            });

            points_to_remove_ids.forEach(function(i) {
                self.markersLayer.removeLayer(self.markers[i]);
                delete self.markers[i];
                delete self.markersData[i];
            });

            $.each(points_to_proccess, function(index, point) {

                var geoJsonLayer = L.geoJSON(point, {
                    pointToLayer: function (feature, latlng) {
                        if (self.useSVGMarkers){
                            var icon = self.getMarkerIcon(feature.properties.icon);
                            var marker = L.marker(latlng, {icon: icon});
                        } else {
                            var marker = L.marker(latlng);
                        }
                        self.markers[feature.properties.id] = marker;
                        self.markersData[feature.properties.id] = {
                            'icon_color': feature.properties.color
                        };
                        return marker;
                    },
                    onEachFeature: function (feature, layer) {
                        layer.on('click', function (e) {
                            self.markerClick(feature.properties.id, feature.geometry.coordinates);
                        });
                    }
                });

                self.markersLayer.addLayer(geoJsonLayer);
                // }
            });
        },

        setDefaultMarkers: function(points) {
            let self = this;

            $.each(points, function(index, point) {
                var geoJsonLayer = L.geoJSON(point, {
                    pointToLayer: function (feature, latlng) {
                        if (self.useSVGMarkers){
                            var icon = self.getMarkerIcon(feature.properties.icon);
                            var marker = L.marker(latlng, {icon: icon});
                        } else {
                            var marker = L.marker(latlng);
                        }
                        return marker;
                    },
                    onEachFeature: function (feature, layer) {
                        layer.on('click', function (e) {
                            self.markerClick(feature.properties.id, feature.geometry.coordinates);
                        });
                    }
                });

                if (point['properties']['id'] in self.markers)
                    self.markersLayer.removeLayer(self.markers[point['properties']['id'] ])

                self.markers[point['properties']['id']] = geoJsonLayer;
                geoJsonLayer.addTo(self.markersLayer);
            });
        },

        getMarkerIcon: function(iconSVG) {
            var icon = L.divIcon({
                className: "leaflet-data-marker",
                html: L.Util.template(iconSVG, {mapIconUrl: iconSVG}),
                iconAnchor  : [20, 20],
                iconSize    : [40, 40],
                popupAnchor : [0, -20]
            });

            return icon;
        },

        markerClick: function(id, coordinates) {

            axios.post('click/', {'id': id, 'coordinates': coordinates, 'theme': this.currentTheme},
            {
                headers: {'X-CSRFToken': csrf_token}
            }).then(response => {
                $("#detail_title").html(response.data.title);
                $("#detail_info").html(response.data.info);
                $("#info_area_container .box-body").addClass("custom-padding")
                $("#info-area-icon").attr('style','padding-top: 7px;')
                info_area_control.increaseAreaControl();
            }).catch((error) => {
                $.notify(error.response.data, {type: 'error'});
            });
        },

        /*** External Call Methods ***/

        resizeMap: function() {
            var containerHeight = $('#map_container').height();
            $("#map").height(containerHeight - 2);
            this.map.invalidateSize();
        },

        searchPoint: function(text, callback) {
            return axios.get('search/?q=' + text+'&theme='+this.currentTheme,
            {
                headers: {'X-CSRFToken': csrf_token}
            }).then(response => {
                callback(response.data.points);
            }).catch((error) => {
                $.notify(error.response.data, {type: 'error'});
            });
        },

        changeTheme: function(el) {
            if (el.value)
                this.currentTheme = el.value;
        },

        clearMap: function() {
            if (this.markersLayer) {
                this.markersLayer.clearLayers();
                this.markers = {};
                this.markersData = {};
            }
        }
    }
});

info_area_control = new Vue({
    el: '#info_area_container',
    delimiters: ['[[', ']]'],
    data: {
        info_area_icon: 'fa fa-chevron-up',
        info_area_icon_click: 'info_area_control.increaseAreaControl();',
        info_area_hidden_limit: 10 // Percentage of screen
    },
    mounted() {
        this.decreaseAreaControl();
    },
    methods: {
        handleAreasHeight: function() {
            var screenHeight = $(window).height();
            var containerHeight = $('#info_area_container').height();
            var percentage = (containerHeight * 100) / screenHeight;

            if (percentage <= this.info_area_hidden_limit) {
                this.info_area_icon = 'fa fa-chevron-left';
                this.info_area_icon_click = 'info_area_control.increaseAreaControl();';

                $('#detail_info').hide();

            } else {
                this.info_area_icon = 'fa fa-chevron-down';
                this.info_area_icon_click = 'info_area_control.decreaseAreaControl();';

                $('#detail_info').show();

            }
        },

        increaseAreaControl: function() {
            map_value = window.innerHeight - 510;
            $('#map_container').attr('style','height:' + (map_value) + 'px;');
            $('#info_area_container').attr('style','height:' + (window.innerHeight - map_value - 94) + 'px;');
            map_control.resizeMap();
            this.handleAreasHeight();
        },

        decreaseAreaControl: function() {
            map_value = window.innerHeight - 141;

            let mapContainerStyle = 'height:' + (map_value) + 'px;';
            let infoAreaContainerStyle = 'height:' + (window.innerHeight - map_value - 94) + 'px;';
            infoAreaContainerStyle += ' background: #FFFFFFc9;';

            $('#map_container').attr('style', mapContainerStyle);
            $('#info_area_container').attr('style', infoAreaContainerStyle);

            map_control.resizeMap();
            this.handleAreasHeight();
        }
    }
});
