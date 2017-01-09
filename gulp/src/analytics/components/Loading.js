import React from 'react';
import {Component} from 'react';

class LoadingSpinner extends Component {
  render() {
    return (
      <div id="loading">
        <div className="analytics-loader"></div>
        <div className="loading-overlay"></div>
      </div>
    );
  }
}

export default LoadingSpinner;
