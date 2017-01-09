import React from 'react';
import {Component} from 'react';
import {PieChart, Pie, ResponsiveContainer} from 'recharts';

class SimplePieChart extends Component {
  render() {
    const data = [
      {name: 'Group A', value: 400},
      {name: 'Group B', value: 300},
      {name: 'Group C', value: 300},
      {name: 'Group D', value: 200},
    ];
    return (
      <div style={{width: '100%', height: '500'}}>
        <ResponsiveContainer>
          <PieChart>
            <Pie data={data} fill="#8884d8" label/>
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  }
}

export default SimplePieChart;
