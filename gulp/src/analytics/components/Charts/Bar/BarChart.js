import React from 'react';
import {Component} from 'react';
import {BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer} from 'recharts';
import RotatedXAxisTick from './RotatedXAxisTick';


class SimpleBarChart extends Component {
  render() {
    const {chartData, width, height, pathClicked} = this.props;
    const barData = chartData.PageLoadData.rows;
    const xAxis = chartData.PageLoadData.column_names[0].key;
    const barClicked = (xAxis) => {
      return (bar) => {pathClicked(bar.activeLabel, xAxis)};
    };
    return (
      <div style={{width: '100%', height: '500'}}>
        <ResponsiveContainer>
          <BarChart
            width={width}
            height={height}
            data={barData}
            margin={{top: 5, right: 30, left: 20, bottom: 100}}
            onClick={barClicked(xAxis)}>
           <XAxis dataKey={xAxis} interval={0} tick={<RotatedXAxisTick />} />
           <YAxis/>
           <CartesianGrid strokeDasharray="3 3" />
           <Tooltip/>
           <Legend verticalAlign="top" wrapperStyle={{top: '0px'}} />
           <Bar dataKey="job_views" fill="#5a6d81" />
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
  /**
   * pathClicked is a function to be called when a path on the chart is clicked
   */
  pathClicked: React.PropTypes.func
};

export default SimpleBarChart;
