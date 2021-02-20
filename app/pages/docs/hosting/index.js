import Layout from '../../../components/layout'
import Highlight from 'react-highlight'

export async function getStaticProps (context) {
  return {
    props: {} // will be passed to the page component as props
  }
}

function Docs ({ params }) {
  return (
    <Layout title='Hosting Documentation: Open Coverage'>
      <div className='container'>
        <br />
        <h1 className='title'>Open Coverage Documentation: Hosting</h1>
        <p className='subtitle'>Host Open Coverage on-prem</p>

        <div className='notification'>
          Open Coverage is distributed as 2{' '}
          <a href='https://hub.docker.com/u/opencoverage' target='_blank'>
            Docker containers
          </a>
          . One for the frontend and one for the API server.
        </div>

        <div className='section'>
          <h2 className='title'>Create GitHub Application</h2>
          <p>
            To run Open Coverage, you will need to create your own GitHub
            application.
          </p>
          <div className='section'>
            <p className='subtitle'>Required permissions</p>
            <table className='table'>
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Access</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Checks</td>
                  <td>Read & Write</td>
                </tr>
                <tr>
                  <td>Contents</td>
                  <td>Read & Write</td>
                </tr>
                <tr>
                  <td>Issues</td>
                  <td>Read & Write</td>
                </tr>
                <tr>
                  <td>Pull Requests</td>
                  <td>Read & Write</td>
                </tr>
                <tr>
                  <td>Commit statuses</td>
                  <td>Read</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p>
            After your app is created, you will need to make sure to download
            the private key file. Open Coverage will use this to authorize
            requests to the GitHub API.
          </p>
          <p>
            <img src='/docs/private-key.png' />
          </p>
        </div>
        <div className='section'>
          <h2 className='title'>Dependencies</h2>
          <div className='content'>
            <p>There are 3 requirements to run Open Coverage:</p>
            <ul>
              <li>
                <b>Database</b> (<a href='https://www.postgresql.org/' target='_blank'>
                PostgreSQL</a> is recommended)
              </li>
              <li>
                <b>API Server</b>
              </li>
              <li>
                <b>Frontend</b>
              </li>
            </ul>
            {/* prettier-ignore */}
            <Highlight className='yml'>
{`
version: "2"
services:
  postgres:
    image: postgres:12
    ports:
      - 5432:5432
    expose:
      - 5432
    environment:
      POSTGRES_USER: opencoverage
      POSTGRES_PASSWORD: secret
      POSTGRES_INITDB_ARGS: --data-checksums
      POSTGRES_DB: opencoverage

  api:
    # image: opencoverage/api:latest
    build:
      context: .
    ports:
      - 8000:8000
    expose:
      - 8000
    environment:
      PUBLIC_URL: http://localhost:3000
      DSN: postgresql://opencoverage:secret@postgres:5432/opencoverage?sslmode=disable
      SCM: github
      GITHUB_APP_PEM_FILE: /app/cov.pem
      GITHUB_APP_ID: "[your github app id]"
      GITHUB_DEFAULT_INSTALLATION_ID: "[your installation id]"
      ROOT_PATH: /api
      CORS: '["http://localhost:8080"]'
    volumes:
      - ${`{PWD}`}/cov.pem:/app/cov.pem
    depends_on:
      - postgres
    links:
      - postgres

  frontend:
    image: opencoverage/frontend:latest
    build:
      context: app
    ports:
      - 3000:3000
    expose:
      - 3000
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/
    depends_on:
      - api
    links:
      - api
`}
            </Highlight>
            {/* prettier-ignore-end */}
          </div>
        </div>
        <div className='section'>
          <p className='subtitle'>API Environments Variable Configuration</p>
          <table className='table'>
            <thead>
              <tr>
                <th>Name</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>HOST</td>
                <td>Host to startup on. Defaults to <span className='tag'>0.0.0.0</span></td>
              </tr>
              <tr>
                <td>ROOT_PATH</td>
                <td>Path API is exposed at. Defaults of <span className='tag'>/</span></td>
              </tr>
              <tr>
                <td>PUBLIC_URL</td>
                <td>Public URL of API</td>
              </tr>
              <tr>
                <td>CORS</td>
                <td>List of domains API should be allowed on</td>
              </tr>
              <tr>
                <td>DSN</td>
                <td>Database connection string</td>
              </tr>
              <tr>
                <td>SCM</td>
                <td>Only supported SCM value is <span className='tag'>github</span> right now</td>
              </tr>
              <tr>
                <td>GITHUB_APP_ID</td>
                <td>ID of GitHub Application</td>
              </tr>
              <tr>
                <td>GITHUB_APP_PEM_FILE</td>
                <td>Path to pem file with private key</td>
              </tr>
              <tr>
                <td>GITHUB_DEFAULT_INSTALLATION_ID</td>
                <td>
                  Installation ID to use if <span className='tag'>-</span> given for <span className='tag'>--token</span> value in
                  codecov upload
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className='section'>
          <p className='subtitle'>
            Frontend Environments Variable Configuration
          </p>
          <table className='table'>
            <thead>
              <tr>
                <th>Name</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>NEXT_PUBLIC_API_URL</td>
                <td>URL of public API service</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className='section'>
          <h2 className='title'>Serving with NGINX</h2>
          <div className='content'>
            <p>Use <a href='https://www.nginx.com/' target='_blank'>
                NGINX</a> to serve Frontend and API:</p>
            {/* prettier-ignore */}
            <Highlight className='yml'>
{`
version: "2"
services:
...
  nginx:
    image: nginx:1.19.7
    restart: always
    volumes:
      - ${`{PWD}`}/conf/nginx-templates:/etc/nginx/templates
    ports:
      - 80:80
    expose:
      - 80
    depends_on:
      - api
      - frontend
    links:
      - api
      - frontend
...
`}
            </Highlight>
            {/* prettier-ignore-end */}
          </div>
          <p>
            Where the file <span className='tag'>conf/nginx-templates/default.conf.template</span>
            contains:
          </p>
          <br></br>
          {/* prettier-ignore */}
          <Highlight className='yml'>
{`
  upstream api {
    server api:8000;
  }
  server {
      listen       80;
      listen  [::]:80;
      server_name  _;

      client_max_body_size 100M;
      location / {
          proxy_pass http://frontend:3000;
      }

      location /api/ {
        proxy_pass_header Server;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme https;  // set scheme here
        proxy_set_header X-Forwarded-Proto https;
        proxy_pass http://api/;
      }
  }
`}
            </Highlight>
          {/* prettier-ignore-end */}
          <p>
            This will expose the frontend at the root of the site and the API
            server at <span className='tag'>/api</span>.
          </p>
        </div>
      </div>
    </Layout>
  )
}

export default Docs
