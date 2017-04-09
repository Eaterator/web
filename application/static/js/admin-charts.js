// modelled after his directive:
// http://bl.ocks.org/biovisualize/5372077
// and this horizontal chart:
// https://bl.ocks.org/hrecht/f84012ee860cb4da66331f18d588eee3
d3.custom = {};

d3.custom.barChart = function module() {
    var margin = {top: 20, right: 40, bottom: 50, left: 100},
        width = 600,
        height = 1000,
        axisPadding = 5, // padding in pixel
        gap = 0,
        ease = 'cubic-in-out';
    var svg, duration = 500;

    var dispatch = d3.dispatch('customHover');
    function exports(_selection) {
        _selection.each(function(_data, _title) {
            _data.reverse();
            var chartW = width - margin.left - margin.right,
                chartH = height - margin.top - margin.bottom;

            var barW = chartH / _data.length;

            var x = d3.scale.sqrt()
                .domain(d3.extent(_data, function(d) {
                    return d.value;
                }))
                .range([0, chartW]);

            var colorScale = d3.scale.category20c();

            var y = d3.scale.ordinal()
                .domain(_data.map(function(d){
                    return d.name
                }))
                .rangePoints([chartH, 0]);

            var xAxis = d3.svg.axis()
                .scale(x)
                .orient('bottom');

            var yAxis = d3.svg.axis()
                .scale(y)
                .orient('left');

            if(!svg) {
                svg = d3.select(this)
                    .append('svg')
                    .classed('chart', true);
                var container = svg.append('g').classed('container-group', true);
                container.append('g').classed('chart-group', true);
                container.append('g').classed('x-axis-group axis', true);
                container.append('g').classed('y-axis-group axis', true);
            }

            svg.transition().duration(duration).attr({width: width, height: height})
            svg.select('.container-group')
                .attr({transform: 'translate(' + margin.left + ',' + margin.top + ')'});

            svg.select('.x-axis-group.axis')
                .transition()
                .duration(duration)
                .ease(ease)
                .attr({transform: 'translate(0,' + chartH + ')'})
                .call(xAxis);

            svg.select('.y-axis-group.axis')
                .transition()
                .duration(duration)
                .ease(ease)
                //.attr({transform: 'translate(0,' + (barW / 2 + axisPadding * 2) + ')'})
                .call(yAxis);

            var bars = svg.select('.chart-group')
                .selectAll('.bar')
                .data(_data);

            bars.enter().append('rect')
                .classed('bar', true)
                // set width and height of bars
                .attr("y", function(d, i){
                    return y(d.name) - barW / 2 ;
                })
                .attr('height',  barW)
                .attr('x', 0)
                .attr("width", function(d) {
                    return x(d.value)
                })
                .style("fill", function(d, i) {
                    return colorScale(i);
                });

            bars.enter().append('text')
                .attr("class", "label")
                // position y label vertically
                .attr('y', function(d, i){
                    return y(d.name) + barW / 4 ;//y.rangeBand() / 2 + 4;
                })
                // position x to the left of the bar
                .attr('x', function(d) {
                    return x(d.value) + axisPadding;
                })
                .text(function (d) {
                    return d.value;
                });

            // add title
            svg.append("text")
                .attr("x", (chartW / 2))
                .attr("y", 0 - (margin.top / 2))
                .attr("text-anchor", "middle")
                .style("font-size", "16px")
                .style("text-decoration", "underline")
                .text(_title);
        });
    }
    exports.width = function(_x) {
        if (!arguments.length) return width;
        width = parseInt(_x);
        return this;
    };
    exports.height = function(_x) {
        if (!arguments.length) return height;
        height = parseInt(_x);
        duration = 0;
        return this;
    };
    exports.gap = function(_x) {
        if (!arguments.length) return gap;
        gap = _x;
        return this;
    };
    exports.ease = function(_x) {
        if (!arguments.length) return ease;
        ease = _x;
        return this;
    };
    d3.rebind(exports, dispatch, 'on');
    return exports;
};

d3.custom.lineChart = function module() {
    var margin = {top: 20, right: 20, bottom: 50, left: 40},
        width = 500,
        height = 500,
        gap = 0,
        ease = 'cubic-in-out';
    var svg, duration = 500;

    var dispatch = d3.dispatch('customHover');
    function exports(_selection) {
        _selection.each(function(_data, title) {
            console.log(_data);
            var parseDate = d3.time.format("%y-%m-%d").parse

            var chartW = width - margin.left - margin.right,
                chartH = height - margin.top - margin.bottom;

            var x = d3.time.scale()// d3.scale.scaleTime()
                // .domain(_data.map(function(d, i){ return parseDate(d.date); }))
                .domain(d3.extent(_data, function(d, i) {
                    return parseDate(d.date);
                }))
                .range([margin.left, chartW]);
            var yExtent = d3.extent(_data, function(d, i) { return d.value});
            if ((yExtent[1] - yExtent[0]) < 5) {
                yExtent[1] = yExtent[0] + 5
            }
            var y = d3.scale.linear()
                .domain(yExtent)
                .range([chartH, 0]);

            var xAxis = d3.svg.axis()
                .scale(x)
                .tickFormat(d3.time.format("%m-%d"))
                .orient('bottom');

            var yAxis = d3.svg.axis()
                .scale(y)
                .orient('left');


            if(!svg) {
                svg = d3.select(this)
                    .append('svg')
                    .classed('chart', true);
                var container = svg.append('g').classed('container-group', true);
                container.append('g').classed('chart-group', true);
                container.append('g').classed('x-axis-group axis', true);
                container.append('g').classed('y-axis-group axis', true);
            }

            svg.transition().duration(duration).attr({width: width, height: height})
            svg.select('.container-group')
                .attr({transform: 'translate(' + margin.left + ',' + margin.top + ')'});

            svg.select('.x-axis-group.axis')
                .transition()
                .duration(duration)
                .ease(ease)
                .attr({transform: 'translate(' + -margin.left + ',' + (chartH) + ')'})
                .call(xAxis)
                .selectAll("text")
                    .style("text-anchor", "end")
                    .attr("dx", "-.8em")
                    .attr("dy", ".15em")
                    .attr("transform", "rotate(-45)" );

            svg.select('.y-axis-group.axis')
                .transition()
                .duration(duration)
                .ease(ease)
                .attr({transform: 'translate(' - margin.left + ', 0)' })
                .call(yAxis);

            var lines = svg.select('.chart-group')
                .selectAll('.line')
                .data(_data);

            var line = d3.svg.line()
                .x(function(d, i) {
                    return x(parseDate(d.date));
                })
                .y(function(d, i) {
                    return y(d.value);
                })
                .interpolate('monotone');

            svg.append('svg:path')
                .attr('d', line(_data))
                .attr('stroke', 'blue')
                .attr('stroke-width', 2)
                .attr('fill', 'none');

            // add title
            svg.append("text")
                .attr("x", (chartW / 2))
                .attr("y", 0 - (margin.top / 2))
                .attr("text-anchor", "middle")
                .style("font-size", "16px")
                .style("text-decoration", "underline")
                .text(title);

        });
    }
    exports.width = function(_x) {
        if (!arguments.length) return width;
        width = parseInt(_x);
        return this;
    };
    exports.height = function(_x) {
        if (!arguments.length) return height;
        height = parseInt(_x);
        duration = 0;
        return this;
    };
    exports.gap = function(_x) {
        if (!arguments.length) return gap;
        gap = _x;
        return this;
    };
    exports.ease = function(_x) {
        if (!arguments.length) return ease;
        ease = _x;
        return this;
    };
    d3.rebind(exports, dispatch, 'on');
    return exports;
};