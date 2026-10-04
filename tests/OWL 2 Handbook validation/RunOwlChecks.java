import java.nio.file.*;
import java.util.*;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.profiles.*;
import org.semanticweb.owlapi.reasoner.*;
import org.semanticweb.HermiT.Reasoner;

/** Run with Java 17 source-file mode and the pinned ROBOT dependency bundle. */
class RunOwlChecks {
  static String safe(Object s) {return String.valueOf(s).replace('\t',' ').replace('\n',' ').replace('\r',' ');}
  public static void main(String[] args) throws Exception {
    if(args.length!=1) throw new IllegalArgumentException("Expected one case directory");
    Path root=Paths.get(args[0]);
    Set<String> ids=new HashSet<>();
    List<String> out=new ArrayList<>();
    List<String> log=new ArrayList<>();
    out.add("id\tprofile_actual\tprofile_expected\tconsistent\tconsistent_expected\tentailment\tentailment_expected\tstatus\tdiagnostics");
    System.out.println("Java: "+System.getProperty("java.version"));
    System.out.println("OWLAPI: "+org.semanticweb.owlapi.util.VersionInfo.getVersionInfo());
    System.out.println("HermiT: "+new Reasoner.ReasonerFactory().getReasonerName());
    Properties hermitMetadata=new Properties();
    try(var in=RunOwlChecks.class.getClassLoader().getResourceAsStream("META-INF/maven/net.sourceforge.owlapi/org.semanticweb.hermit/pom.properties")) {
      if(in!=null) hermitMetadata.load(in);
    }
    System.out.println("HermiT dependency artifact: "+hermitMetadata.getProperty("version","unknown"));
    log.add("Java: "+System.getProperty("java.version"));
    log.add("OWLAPI: "+org.semanticweb.owlapi.util.VersionInfo.getVersionInfo());
    log.add("HermiT dependency artifact: "+hermitMetadata.getProperty("version","unknown"));
    int passed=0, failures=0;
    for(String line:Files.readAllLines(root.resolve("owl_tasks.tsv"))) {
      if(line.startsWith("#") || line.isBlank()) continue;
      String[] t=line.split("\t",-1); String id=t[0];
      if(t.length!=6 || !ids.add(id)) throw new IllegalArgumentException("Malformed or duplicate task: "+line);
      boolean expectedProfile=Boolean.parseBoolean(t[2]);
      String consistency="SKIPPED", entailment="SKIPPED", status="PASS", diagnostic="";
      Boolean profile=null; OWLReasoner reasoner=null;
      try {
        OWLOntologyManager manager=OWLManager.createOWLOntologyManager();
        OWLOntology ontology=manager.loadOntologyFromOntologyDocument(root.resolve(t[1]).toFile());
        OWLProfileReport report=new OWL2DLProfile().checkOntology(ontology);
        profile=report.isInProfile(); diagnostic=report.getViolations().toString();
        if(profile!=expectedProfile) status="FAIL";
        if(profile) {
          reasoner=new Reasoner.ReasonerFactory().createReasoner(ontology);
          diagnostic += " reasoner="+reasoner.getReasonerName()+" version="+reasoner.getReasonerVersion();
          boolean consistent=reasoner.isConsistent(); consistency=String.valueOf(consistent);
          if(!t[3].isEmpty() && consistent!=Boolean.parseBoolean(t[3])) status="FAIL";
          if(consistent && !t[4].isEmpty()) {
            OWLOntology query=OWLManager.createOWLOntologyManager().loadOntologyFromOntologyDocument(root.resolve(t[4]).toFile());
            if(query.getLogicalAxioms().size()!=1) throw new IllegalArgumentException("Query must contain exactly one logical axiom");
            OWLAxiom ax=query.getLogicalAxioms().iterator().next();
            if(!reasoner.isEntailmentCheckingSupported(ax.getAxiomType())) throw new UnsupportedOperationException("Unsupported query type "+ax.getAxiomType());
            boolean entailed=reasoner.isEntailed(ax); entailment=String.valueOf(entailed);
            if(entailed!=Boolean.parseBoolean(t[5])) status="FAIL";
          }
        }
      } catch(Exception e) {status="ERROR"; diagnostic=e.toString();}
      finally {if(reasoner!=null) reasoner.dispose();}
      out.add(id+"\t"+profile+"\t"+expectedProfile+"\t"+consistency+"\t"+t[3]+"\t"+entailment+"\t"+t[5]+"\t"+status+"\t"+safe(diagnostic));
      System.out.println(id+" "+status);
      log.add(id+" "+status+" "+safe(diagnostic));
      if(status.equals("PASS")) passed++; else failures++;
    }
    Files.write(root.resolve("owl_results.tsv"),out);
    System.out.println("Passed="+passed+" failures="+failures);
    log.add("Passed="+passed+" failures="+failures);
    Files.write(root.resolve("owl_run.log"),log);
    if(failures>0) System.exit(1);
  }
}
