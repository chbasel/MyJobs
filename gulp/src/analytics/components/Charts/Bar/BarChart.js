import React from 'react';
import {Component} from 'react';
import d3 from 'd3';
import {BarChart, Cell, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer} from 'recharts';
import RotatedXAxisTick from './RotatedXAxisTick';


class SimpleBarChart extends Component {
  render() {
    const {chartData, width, height} = this.props;
    const barData = chartData.PageLoadData.rows;
    const xAxis = chartData.PageLoadData.column_names[0].key;
    const ranges = ['rgb(103,0,13)', 'rgb(165,15,21)', 'rgb(203,24,29)', 'rgb(239,59,44)', 'rgb(251,106,74)', 'rgb(252,146,114)', 'rgb(252,187,161)', 'rgb(254,224,210)', 'rgb(255,245,240)', 'rgb(255,245,235)'];
    const colors = d3.scale.ordinal().range(ranges);
    return (
      <div style={{width: '100%', height: height}}>
        <ResponsiveContainer>
          <BarChart
            width={width}
            height={height}
            data={barData}
            margin={{top: 5, right: 30, left: 20, bottom: 100}}>
           <XAxis dataKey={xAxis} interval={0} tick={<RotatedXAxisTick />} />
           <YAxis/>
           <CartesianGrid strokeDasharray="3 3" />
           <Tooltip/>
           <Legend verticalAlign="top" wrapperStyle={{top: '0px'}} />
           <Bar maxBarSize={75} name="Job Views" dataKey="job_views" fill="#5A6D81">
             {
               barData.map((entry, index) => (
                 <Cell key={index} fill={colors(entry.job_views)}/>
               ))
             }
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }
}

SimpleBarChart.propTypes = {
  /**
   * Type of object representing the data going into the object
   */
  chartData: React.PropTypes.object.isRequired,
  /**
   * Type is a number for the height of the chart
   */
  height: React.PropTypes.number.isRequired,
  /**
   * Type is a number value for the width of the chart
   */
  width: React.PropTypes.number.isRequired,
};

export default SimpleBarChart;
