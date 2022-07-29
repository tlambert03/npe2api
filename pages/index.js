import fs from "fs";
import path from "path";
import Link from "next/link";

export default function home({ data }) {
  return (
    <div>
      <h1>napari plugins</h1>
      <h3>(this page is for humans)</h3>
      <p><Link href={`/errors.json`}><a>fetch errors</a></Link></p>
      <p><Link href={`/api/plugins`}><a>plugins summary</a></Link></p>
      <h4>manifests</h4>
      <ul>
        {data.map((item) => (
          <li key={item.name}>
            <Link
              as={`/api/manifest/${item.name}`}
              href={`/api/manifest/[slug]`}
            >
              <a>
                {item.name}-{item.version}
              </a>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export const getStaticProps = async () => {
  const source = fs.readFileSync(
    path.join(process.cwd(), "public", "index.json")
  );
  return {
    props: {
      data: JSON.parse(source),
    },
  };
};
