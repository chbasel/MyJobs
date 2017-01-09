import d3 from 'd3';
import React from 'react';
import ReactDOM from 'react-dom';


const Axis = React.createClass({
  propTypes: {
    height: React.PropTypes.number,
    width: React.PropTypes.number,
    axis: React.PropTypes.func,
    axisType: React.PropTypes.oneOf(['x', 'y']),
  },
  componentDidMount() {
    this.renderAxis();
  },
  componentDidUpdate() {
    this.renderAxis();
  },
  renderAxis() {
    const node = ReactDOM.findDOMNode(this);
    d3.select(node).call(this.props.axis);
  },
  render() {
    const translate = 'translate(0,' + (this.props.height) + ')';
    const xLabel = 'Days';
    const transformYLabel = 'translate(-50,' + this.props.height / 2 + ') rotate(-90)';
    const transformXLabel = 'translate(' + this.props.width / 2 + ',60)';
    if (this.props.axisType === 'x') {
      return (
        <g className="axis" transform={translate} >
          <text
            x={0}
            y={0}
            transform={transformXLabel}
            className="chart-legend"
          >
          {xLabel}
          </text>
        </g>
      );
    } else if (this.props.axisType === 'y') {
      return (
        <g className="axis" transform={''} >
          <text
            x={0}
            y={0}
            transform={transformYLabel}
            className="chart-legend"
          >
          </text>
        </g>
      );
    }
  },
});

export default Axis;
