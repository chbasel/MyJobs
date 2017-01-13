import React from 'react';
import {Component} from 'react';

class PageSize extends Component {
  render() {
    const {pageSize, handlePageSizeChange, showCount} = this.props;
    const options = showCount.map((show, i) => {
      return (
        <option key={i} value={show}>{show}</option>
      );
    });
    return (
      <div>
        <label htmlFor="pageSize">Per Page: </label>
        <select className="page-size" value={pageSize} onChange={handlePageSizeChange}>
          {options}
        </select>
      </div>
    );
  }
}

PageSize.propTypes = {
  /**
   * Number supplied for the value of the select box
   */
  pageSize: React.PropTypes.number.isRequired,
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
