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

export default PageSize;
