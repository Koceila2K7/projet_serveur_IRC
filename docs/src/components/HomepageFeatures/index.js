import React from "react";
import clsx from "clsx";
import styles from "./styles.module.css";

const FeatureList = [
  {
    title: "Introduction à la blockchain",
    png: require("@site/static/img/blockchain.png").default,
    description: (
      <>Ce projet introduit le cours de blockchain du master ISD Paris Saclay</>
    ),
  },
  {
    title: "Implémentation en mode client serveur",
    png: require("@site/static/img/socket.png").default,
    description: (
      <>Nous avons implémenté deux version dont une client-serveur</>
    ),
  },
  {
    title: "Mise en place d'un réseau Pair-à-pair",
    png: require("@site/static/img/peer_to_peer.png").default,
    description: <>Nous avons implémenté une version P2P du projet</>,
  },
];

function Feature({ Svg, title, description, png }) {
  return (
    <div className={clsx("col col--4")}>
      <div className="text--center">
        {Svg && <Svg className={styles.featureSvg} role="img" />}
        {png && <img src={png} className={styles.featureSvg} />}
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
