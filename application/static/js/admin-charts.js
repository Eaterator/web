// modelled after his directive:
// http://bl.ocks.org/biovisualize/5372077
// and this horizontal chart:
// https://bl.ocks.org/hrecht/f84012ee860cb4da66331f18d588eee3
d3.custom = {};

d3.custom.barChart = function module() {
    var margin = {top: 0, right: 0, bottom: 0, left: 0},
        width = 500,
        height = 1000,
        chartAreaBuffer = 0.95;
        gap = 0,
        ease = 'cubic-in-out';
    var svg, duration = 500;

    var dispatch = d3.dispatch('customHover');
    function exports(_selection) {
        _selection.each(function(_data) {
            console.log('d3 here');
            console.log(_data);
            var chartW = width - margin.left - margin.right,
                chartH = height - margin.top - margin.bottom;
            var x = d3.scale.linear()
                .domain(d3.extent(_data, function(d) {
                    return d.value;
                }))
                .range([0, chartW]);

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

            var barW = chartH / (_data.length * 1.1);

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
                .attr({transform: 'translate(0,' + (chartH) + ')'})
                .call(xAxis);

            svg.select('.y-axis-group.axis')
                .transition()
                .duration(duration)
                .ease(ease)
                .attr({transform: 'translate(0,' + barW / 2 + ')'})
                .call(yAxis);

            var bars = svg.select('.chart-group')
                .selectAll('.bar')
                .data(_data);

            bars.enter().append('rect')
                .classed('bar', true)
                // set width and height of bars
                .attr("y", function(d, i){
                    return y(d.name);
                })
                .attr('height',  barW)
                .attr('x', 0)
                .attr("width", function(d) {
                    return x(d.value)
                });

            bars.enter().append('text')
                .attr("class", "label")
                // position y label vertically
                .attr('y', function(d, i){
                    return y(d.name) + barW /2 ;//y.rangeBand() / 2 + 4;
                })
                // position x to the left of the bar
                .attr('x', function(d) {
                    return x(d.value);
                })
                .text(function (d) {
                    return d.value;
                });
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
    var margin = {top: 20, right: 20, bottom: 40, left: 40},
        width = 500,
        height = 500,
        gap = 0,
        ease = 'cubic-in-out';
    var svg, duration = 500;

    var dispatch = d3.dispatch('customHover');
    function exports(_selection) {
        _selection.each(function(_data) {
            var formatDate = d3.time.format("%d-%b-%y");
            var parseTime = formatDate.parse;// d3.timeParse('%y-%m-%d');

            var chartW = width - margin.left - margin.right,
                chartH = height - margin.top - margin.bottom;

            var x = d3.time.scale()// d3.scale.scaleTime()
                .domain(_data.map(function(d, i){ return d.date; }))
                // .rangeRoundBands([0, chartW], .1);

            var y = d3.scale.ordinal()
                .domain([0, d3.max(_data, function(d, i){ return d.value; })])
                .range([chartH, 0]);

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
                .attr({transform: 'translate(0,' + (chartH) + ')'})
                .call(xAxis);

            svg.select('.y-axis-group.axis')
                .transition()
                .duration(duration)
                .ease(ease)
                .call(yAxis);

            var line = d3.svg.line()
                .x(function(d, i) {
                    return x(parseTime(d.date));
                })
                .y(function(d, i) {
                    return y(d.value);
                });

           var lines = svg.select('.chart-group')
                .selectAll('.line')
                .data(_data);

           lines.enter().append('path')
                .classed('line', true)
                .attr('d', line);
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