import React from 'react';
import {Component} from 'react';

class PageSize extends Component {
  switchToStartPage(e) {
    const {handlePageSizeChange, handlePageChange, currentPage} = this.props;
    if (currentPage !== 1) {
      handlePageChange(1);
      handlePageSizeChange(e);
    } else {
      handlePageSizeChange(e);
    }
  }
  render() {
    const {showCount} = this.props;
    const options = showCount.map((show, i) => {
      return (
        <option key={i} value={show}>{show}</option>
      );
    });
    return (
      <div className="page-size-container">
        <span className="show-page-size">Show:</span>
        <select className="page-size" onChange={this.switchToStartPage.bind(this)}>
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
  /**
   * Function supplied in order to change the amount of data shown per page on the page size component
   */
  handlePageChange: React.PropTypes.func,
  /**
   * Current page is a number that shows which page of the pagination is initially shown when the table renders
   */
  currentPage: React.PropTypes.number.isRequired,
};

export default PageSize;
