import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';

class Header extends Component {
  render() {
    return (
      <div className="tabs-header">
        <nav>
          <i className="open-mobile fa fa-arrow-circle-right" aria-hidden="true"></i>
          <ul className="nav navbar-nav navbar-right right-options">
            <li><a href="#"><span className="head-icon fa fa-envelope-o"></span></a></li>
            <li><a href="#"><span className="head-icon fa fa-print"></span></a></li>
            <li><a href="#"><span className="head-icon fa fa-file-excel-o"></span></a></li>
          </ul>
        </nav>
      </div>
    );
  }
}

export default connect(state => ({
  analytics: state.pageLoadData,
}))(Header);
