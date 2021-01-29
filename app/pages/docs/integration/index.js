import Layout from '../../../components/layout'
import { useState } from 'react'
import Highlight from 'react-highlight'

function InstallOpenCoverage ({ params }) {
  return (
    <>
      <h2 className='title'>Install Open Coverage GitHub Application</h2>
      <div class='message is-dark'>
        <div class='message-body'>
          Before you can submit your coverage to the public Open Coverage
          service, you need install the application for your organization.
        </div>
      </div>
      <p>
        Visit the{' '}
        <a href='https://github.com/apps/open-coverage' target='_blank'>
          GitHub App
        </a>{' '}
        and install it for your organization.
      </p>
      <div className='section'>
        <p className='buttons'>
          <a
            target='_blank'
            className='button is-link is-large'
            href='https://github.com/apps/open-coverage'
          >
            <span className='icon is-medium'>
              <i className='fab fa-github'></i>
            </span>
            <span>Install open coverage</span>
          </a>
        </p>
      </div>
      <p>
        After you install the application to your organization, pay attention to
        the installation id for your organization. You will be using this as a
        token when you upload your coverage report.
      </p>
      <p>
        <img src='/docs/install-id.png' />
      </p>
    </>
  )
}

function GenerateCoverage ({ params }) {
  var [lang, setTab] = useState(0)
  if (!lang) {
    lang = 'python'
  }

  return (
    <>
      <div className='tabs'>
        <ul>
          <li className={lang == 'python' ? 'is-active' : ''}>
            <a onClick={() => setTab('python')}>Python</a>
          </li>
          <li className={lang == 'js' ? 'is-active' : ''}>
            <a onClick={() => setTab('js')}>JavaScript</a>
          </li>
          <li className={lang == 'java' ? 'is-active' : ''}>
            <a onClick={() => setTab('java')}>Java</a>
          </li>
        </ul>
      </div>
      <div className={lang == 'python' ? '' : 'is-hidden'}>
        Use the python <a href='https://coverage.readthedocs.io/'>Coverage</a>{' '}
        coverage package to generate an xml coverage report.
        <br />
        Once `coverage` is installed, you just need to produce the xml report.
        <Highlight className='sh'>coverage xml</Highlight>
        <br />
        If you're using `pytest`, you can also integrate with `pytest-cov` to
        generate it all with once command.
        <br />
        <Highlight className='sh'>
          pytest tests --cov=[mypackage] --cov-report xml
        </Highlight>
      </div>
      <div className={lang == 'js' ? '' : 'is-hidden'}>...</div>
      <div className={lang == 'java' ? '' : 'is-hidden'}>...</div>
    </>
  )
}

function Docs ({ params }) {
  const [tab, setCount] = useState(0)

  return (
    <Layout title='Integration Documentation: Open Coverage'>
      <div className='container'>
        <br />
        <h1 className='title'>Open Coverage Documentation</h1>
        <p className='subtitle'>
          Integration: Use the public open coverage service
        </p>

        <div className='notification is-danger'>
          Do not integrate with private repositories. Use the self-hosted option
          for private repositories.
        </div>

        <div className='section'>
          <InstallOpenCoverage />
        </div>

        <div className='section'>
          <h2 className='title'>Generate coverage data</h2>
          <div className='message is-dark'>
            <div className='message-body'>
              Next, you'll need to generate coverage data for your test runs.
              This will look different depending on the language you're
              developing with.
            </div>
          </div>
          <GenerateCoverage />
        </div>
        <div className='section'>
          <h2 className='title'>Submit coverage</h2>
          <div className='message is-dark'>
            <div className='message-body'>
              Finally, you need to submit your coverage data to Open Coverage
            </div>
          </div>
          <p>
            The tested method for submitting coverage data is through the python
            codecov module.
          </p>
          <Highlight className='sh'>pip install codecov</Highlight>
          Then, submit with custom URL:
          <Highlight className='sh'>
            codecov --url="https://open-coverage.org/api" --token=[github
            installation id] --slug=[org]/[repo]
          </Highlight>
          <div className='section'>
            <p className='subtitle'>Configuration</p>
            <table className='table'>
              <thead>
                <tr>
                  <th>Option</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <b>--token</b>
                  </td>
                  <td>Open Coverage installation id for your organization</td>
                </tr>
                <tr>
                  <td>
                    <b>--slug</b>
                  </td>
                  <td>
                    Should be <span className='tag'>[org]/[repo]</span>{' '}
                    combination for your repository. For example,{' '}
                    <span className='tag'>vercel/next.js`</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default Docs
