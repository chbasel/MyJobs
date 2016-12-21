import React from 'react';
import {Component} from 'react';
import moment from 'moment';

class RangeSelection extends Component {
  constructor(props) {
    super(props);

    this.state = {
      ranges: [
        {name: 'Today', date: [moment().format('MM/DD/YYYY 00:00:00'), moment().format('MM/DD/YYYY H:mm:ss')]},
        {name: 'Yesterday', date: [moment().subtract(1, 'days').format('MM/DD/YYYY 00:00:00'), moment().subtract(1, 'days').format('MM/DD/YYYY 23:59:59')]},
        {name: 'Last 7 Days', date: [moment().subtract(6, 'days').format('MM/DD/YYYY 00:00:00'), moment().format('MM/DD/YYYY H:mm:ss')]},
        {name: 'Last 30 Days', date: [moment().subtract(29, 'days').format('MM/DD/YYYY 00:00:00'), moment().format('MM/DD/YYYY H:mm:ss')]},
        {name: 'This Month', date: [moment().startOf('month').format('MM/DD/YYYY 00:00:00'), moment().endOf('month').format('MM/DD/YYYY H:mm:ss')]},
        {name: 'Last Month', date: [moment().subtract(1, 'month').startOf('month').format('MM/DD/YYYY 00:00:00'), moment().subtract(1, 'month').endOf('month').format('MM/DD/YYYY 23:59:59')]},
      ],
    };
  }
  render() {
    const {setRange, showCustomRange, cancelSelection} = this.props;
    const generateRanges = this.state.ranges.map((range, i) => {
      return (
        <li key={i} className="range" onClick={() => setRange(range.date)}>{range.name}</li>
      );
    });
    return (
      <div className="range-container">
        <ul className="range-selections">
          {generateRanges}
          <li onClick={() => showCustomRange()} className="range">Custom Range</li>
          <li className="apply-cancel"><button className="range-btn apply-range">APPLY</button><button onClick={cancelSelection} className="range-btn cancel-range">CANCEL</button></li>
        </ul>
      </div>
    );
  }
}

RangeSelection.propTypes = {
  /**
   * Set Range is a function on the list items passing the range of dates used
   */
  setRange: React.PropTypes.func.isRequired,
  /**
   * Function passed to show the calendar when a custom range is clicked
   */
  showCustomRange: React.PropTypes.func,
  /**
   * Closes the calendar and cancels the date change
   */
  cancelSelection: React.PropTypes.func,
};

export default RangeSelection;
