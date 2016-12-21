import React from 'react';
import {Component} from 'react';
import {BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer} from 'recharts';

class SimpleBarChart extends Component {
  render() {
    const {chartData, width, height} = this.props;
    const barData = chartData.PageLoadData.rows;
    // const xAxis = chartData.PageLoadData.column_names[0].key;
    return (
      <div style={{width: '100%', height: '500'}}>
        <ResponsiveContainer>
          <BarChart
            width={width}
            height={height}
            data={barData}
            margin={{top: 5, right: 30, left: 20, bottom: 5}}>
           <XAxis/>
           <YAxis/>
           <CartesianGrid strokeDasharray="3 3"/>
           <Tooltip/>
           <Legend />
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
};

export default SimpleBarChart;
