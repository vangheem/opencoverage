// components/Layout.js
import React, { Component } from 'react'
import Header from './header'
import Footer from './footer'

export default class Layout extends Component {
  render () {
    const { children } = this.props
    return (
      <>
        <div className='layoutwrapper'>
          <Header title={this.props.title} />
          {children}
        </div>
        <Footer />
      </>
    )
  }
}
