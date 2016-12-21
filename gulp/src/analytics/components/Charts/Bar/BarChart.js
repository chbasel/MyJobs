import React from 'react';
import {Component} from 'react';
import {BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer} from 'recharts';

class SimpleBarChart extends Component {
  render() {
    const data = [
          {name: 'Page A', pv: 2400, amt: 2400},
          {name: 'Page B', pv: 1398, amt: 2210},
          {name: 'Page C', pv: 9800, amt: 2290},
          {name: 'Page D', pv: 3908, amt: 2000},
          {name: 'Page E', pv: 4800, amt: 2181},
          {name: 'Page F', pv: 3800, amt: 2500},
          {name: 'Page G', pv: 4300, amt: 2100},
    ];
    return (
      <div style={{width: '100%', height: '500'}}>
        <ResponsiveContainer>
          <BarChart
            width={600}
            height={300}
            data={data}
            margin={{top: 5, right: 30, left: 20, bottom: 5}}>
           <XAxis dataKey="name"/>
           <YAxis/>
           <CartesianGrid strokeDasharray="3 3"/>
           <Tooltip/>
           <Legend />
           <Bar dataKey="pv" fill="#5a6d81" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }
}

export default SimpleBarChart;
