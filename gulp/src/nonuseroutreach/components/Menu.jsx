import React from 'react';
import {Link} from 'react-router';
import {connect} from 'react-redux';
import FilterMenu from './FilterMenu';

/* Menu
 * Component for displaying navigation and tips relevant to the current page.
 */
class Menu extends React.Component {
  render() {
    const {tips, currentPage} = this.props;
    const pageTips = tips.length ? [
      <h2 key="title">Tips</h2>,
      tips.map((tip, i) => <p key={i}>{tip}</p>),
    ] : [];
    const filterMenu = currentPage === 'records' ? <FilterMenu /> : '';

    return (
        <div className="sidebar">
          {filterMenu}
          <h2 className="top">Navigation</h2>
          <Link to="/overview" className="btn">
            Overview
          </Link>
          <Link to="/inboxes" className="btn">
            Inbox Management
          </Link>
          <Link to="/records" className="btn">
            Outreach Records
          </Link>
          <a className="btn" href="http://www.directemployers.org/beta-feedback" target="_blank">Leave Us Feedback</a>
          {pageTips}
        </div>
    );
  }
}

Menu.propTypes = {
  // the tips to be displayed
  tips: React.PropTypes.arrayOf(React.PropTypes.string.isRequired).isRequired,
  currentPage: React.PropTypes.string,
};

export default connect(state => ({
  currentPage: state.navigation.currentPage,
}))(Menu);
