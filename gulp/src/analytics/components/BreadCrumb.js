import React from 'react';
import {Component} from 'react';

class BreadCrumb extends Component {
  render() {
    const {breadcrumbClick, crumbs, id} = this.props;
    const breadcrumbs = crumbs.map((crumb, i) => {
      return (
        <li key={i} onClick={() => breadcrumbClick(crumb)} className="analytics-breadcrumbs">
          <a className={i + 1 === id ? 'crumb-title active-crumb' : 'crumb-title'} href="#">{crumb}</a>
        </li>
      );
    });
    return (
      <ul className="breadcrumb-container">
        {breadcrumbs}
      </ul>
    );
  }
}

BreadCrumb.propTypes = {
  id: React.PropTypes.number.isRequired,
  crumbs: React.PropTypes.array.isRequired,
  breadcrumbClick: React.PropTypes.func,
};

export default BreadCrumb;
