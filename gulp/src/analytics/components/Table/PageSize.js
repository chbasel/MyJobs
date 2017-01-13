import React from 'react';
import {Component} from 'react';

class PageSize extends Component {
  render() {
    const {handlePageSizeChange, showCount} = this.props;
    const options = showCount.map((show, i) => {
      return (
        <option key={i} value={show}>{show}</option>
      );
    });
    return (
      <div className="page-size-container">
        <span className="show-page-size">Show:</span>
        <select className="page-size" onChange={handlePageSizeChange}>
          {options}
        </select>
      </div>
    );
  }
}

PageSize.propTypes = {
  /**
   * Function supplied in order to handle the changing of the page size in the component
   */
  handlePageSizeChange: React.PropTypes.func.isRequired,
  /**
   * Array supplied to the page size in order to handle the options that are available when it comes to the amount of data shown on the table at one time
   */
  showCount: React.PropTypes.array.isRequired,
};

export default PageSize;
